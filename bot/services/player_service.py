from ..services import rcon_service, status_service


async def get_online_players(game):
    await status_service.check_game_is_running(game)
    rcon_client = await rcon_service.get_rcon_client(game)
    players = rcon_client.get_online_players()
    if players == 'Online players (0):':
        return 'There are no currently no players online.'
    return players


async def get_all_players(game):
    await status_service.check_game_is_running(game)
    rcon_client = await rcon_service.get_rcon_client(game)
    players = rcon_client.get_all_players()
    if players == 'Players (0):':
        return 'This game has no players yet.'
    return players
