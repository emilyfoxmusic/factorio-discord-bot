from ..services import ipService
from ..clients import sshClient, rconClient


# A mapping of game to rcon pw. This never needs to be purged as this
# can never change (note this is different to ip which can, and does,
# change).
passwd_cache = {}

async def get_rcon_client(game):
  ip = await ipService.get_ip(game)
  if game not in passwd_cache:
    rcon_pw = sshClient.exec_get(ip, 'cat /opt/factorio/config/rconpw')
    passwd_cache[game] = rcon_pw
  return rconClient.RconClient(ip, passwd_cache[game])