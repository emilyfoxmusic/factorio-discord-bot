from ..exceptions import InvalidOperationException
from ..clients import stack_client
from ..services import mod_service, ip_service, backup_service, server_settings_service
from ..helpers import status_helper
from ..utilities import single


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
    if await get_status(name) == status_helper.Status.DELETING:
        raise InvalidOperationException('Deletion already in progress')
    await stack_client.delete_stack(name)
    ip_service.purge_ip(name)


async def get_status(name):
    stack = await stack_client.stack_details(name)
    return _status_from_stack(stack)


async def start(name):
    status = await get_status(name)
    if status == status_helper.Status.STOPPED or status == status_helper.Status.UNRECOGNISED:
        await stack_client.update_stack(name, 'Running')
    elif status == status_helper.Status.STARTING or status == status_helper.Status.RUNNING:
        raise InvalidOperationException('Server is already running/starting')
    else:
        raise InvalidOperationException(
            'Please wait - another operation is in progress')


async def stop(name, force):
    status = await get_status(name)
    if status == status_helper.Status.RUNNING or status == status_helper.Status.UNRECOGNISED:
        try:
            await backup_service.backup(name)
        except Exception as error:  # pylint: disable=broad-except
            if not force:
                raise InvalidOperationException(
                    "Taking backup failed. If you'd like to stop the server anyway, use " +
                    "`!stop force`") from error
        await stack_client.update_stack(name, 'Stopped')
        ip_service.purge_ip(name)
    elif status == status_helper.Status.STOPPING or status == status_helper.Status.STOPPED:
        raise InvalidOperationException('Server is already stopped/stopping')
    else:
        raise InvalidOperationException(
            'Please wait - another operation is in progress')


async def get_ip(name):
    status = await get_status(name)
    if status == status_helper.Status.RUNNING:
        return await ip_service.get_ip(name)
    else:
        raise InvalidOperationException('Server is not running (yet?)')


async def list_games():
    stacks = await stack_client.list_stacks()
    return {stack['StackName']: _status_from_stack(stack) for stack in stacks}


async def game_exists(name):
    return name in await list_games()


def _status_from_stack(stack):
    server_state_param = single(
        lambda parameter: parameter['ParameterKey'] == 'ServerState', stack['Parameters'])
    return status_helper.get_status(stack['StackStatus'], server_state_param['ParameterValue'])
