from ..services import ip_service
from ..clients import ssh_client, rcon_client


# A mapping of game to rcon pw. This never needs to be purged as this
# can never change (note this is different to ip which can, and does,
# change).
passwd_cache = {}


async def get_rcon_client(game):
    ip = await ip_service.get_ip(game)
    if game not in passwd_cache:
        rcon_pw = ssh_client.execute_get(ip, 'cat /opt/factorio/config/rconpw')
        passwd_cache[game] = rcon_pw
    return rcon_client.RconClient(ip, passwd_cache[game])
