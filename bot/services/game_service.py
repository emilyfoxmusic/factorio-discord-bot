from ..exceptions import InvalidOperationException
from ..clients import stack_client
from ..services import (mod_service, ip_service,
                        backup_service, server_settings_service, status_service)
from ..services.status_service import Status


async def create_game(name, version, *mods):
    if await game_exists(name):
        raise InvalidOperationException('Game already exists')
    # We must check the mods *before* creating the stack in case they are invalid
    # Note this also happens to check the version is syntactically correct, so it's
    # worth running even with no mods.
    mod_releases = await mod_service.get_releases(version, *mods)
    await stack_client.create_stack(name, version)
    if len(mod_releases) > 0:
        await mod_service.install_releases(name, mod_releases)
    await server_settings_service.set_default_settings(name)


async def delete_game(name):
    if not await game_exists(name):
        raise InvalidOperationException('Game not found')
    if await status_service.get_status(name) == status_service.Status.DELETING:
        raise InvalidOperationException('Deletion already in progress')
    await stack_client.delete_stack(name)
    ip_service.purge_ip(name)


async def start(name):
    status = await status_service.get_status(name)
    if status == Status.STOPPED or status == Status.UNRECOGNISED:
        await stack_client.update_stack(name, 'Running')
    elif status == Status.STARTING or status == Status.RUNNING:
        raise InvalidOperationException('Server is already running/starting')
    else:
        raise InvalidOperationException(
            'Please wait - another operation is in progress')


async def stop(name, force):
    status = await status_service.get_status(name)
    if status == Status.RUNNING or status == Status.UNRECOGNISED:
        try:
            await backup_service.backup(name)
        except Exception as error:  # pylint: disable=broad-except
            if not force:
                raise InvalidOperationException(
                    "Taking backup failed. If you'd like to stop the server anyway, use " +
                    "`!stop force`") from error
        await stack_client.update_stack(name, 'Stopped')
        ip_service.purge_ip(name)
    elif status == Status.STOPPING or status == Status.STOPPED:
        raise InvalidOperationException('Server is already stopped/stopping')
    else:
        raise InvalidOperationException(
            'Please wait - another operation is in progress')


async def game_exists(name):
    return name in await status_service.list_game_statuses()
