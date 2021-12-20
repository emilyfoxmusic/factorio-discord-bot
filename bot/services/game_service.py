from factorio_rcon import RCONBaseError
from ..exceptions import InvalidOperationException
from ..clients import stack_client
from ..services import (mod_service, ip_service, player_service,
                        backup_service, server_settings_service, status_service)
from ..services.status_service import Status


async def create_game(game, version, *mods):
    if await game_exists(game):
        raise InvalidOperationException('Game already exists')
    # We must check the mods *before* creating the stack in case they are invalid
    # Note this also happens to check the version is syntactically correct, so it's
    # worth running even with no mods.
    mod_releases = await mod_service.get_releases(version, *mods)
    await stack_client.create_stack(game, version)
    if len(mod_releases) > 0:
        await mod_service.install_releases(game, mod_releases)
    await server_settings_service.set_default_config(game)


async def delete_game(game):
    if not await game_exists(game):
        raise InvalidOperationException('Game not found')
    if await status_service.get_status(game) == status_service.Status.DELETING:
        raise InvalidOperationException('Deletion already in progress')
    await stack_client.delete_stack(game)
    ip_service.purge_ip(game)


async def start(game):
    status = await status_service.get_status(game)
    if status == Status.STOPPED or status == Status.UNRECOGNISED:
        await stack_client.update_stack(game, 'Running')
    elif status == Status.STARTING or status == Status.RUNNING:
        raise InvalidOperationException('Server is already running/starting')
    else:
        raise InvalidOperationException(
            'Please wait - another operation is in progress')


async def stop(game, force):
    status = await status_service.get_status(game)
    if status == Status.RUNNING or status == Status.UNRECOGNISED:
        try:
            players = await player_service.get_online_players(game)
            if players is not None:
                raise InvalidOperationException(
                    "I won't stop the server while someone is playing! :upside_down:")
            await backup_service.backup(game)
        except RCONBaseError as error:
            if not force:
                raise InvalidOperationException(
                    "Failed to connect to the server to check whether there are any online " +
                    "players and to take the backup. If you'd like to stop the server anyway, " +
                    "use `!stop force`") from error
        await stack_client.update_stack(game, 'Stopped')
        ip_service.purge_ip(game)
    elif status == Status.STOPPING or status == Status.STOPPED:
        raise InvalidOperationException('Server is already stopped/stopping')
    else:
        raise InvalidOperationException(
            'Please wait - another operation is in progress')


async def game_exists(game):
    return game in await status_service.list_game_statuses()
