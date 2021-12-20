from ..clients import ec2_client
from ..services import status_service


ip_cache = {}


async def get_ip(game):
    await status_service.check_game_is_running(game)
    if game in ip_cache:
        return ip_cache[game]
    instance = await ec2_client.get_ec2_instance(game)
    ip = instance['PublicIpAddress']
    ip_cache[game] = ip
    return ip


def purge_ip(game):
    if game in ip_cache:
        del ip_cache[game]
