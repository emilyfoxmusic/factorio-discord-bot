from apiclient import JsonResponseHandler
from ..api.modClient import ModClient
from ..exceptions.invalidOperationException import InvalidOperationException
from ..helpers.modHelper import get_release
from ..aws.ecsClient import EcsClient
from .sshService import SshService
from ..helpers.modHelper import download_command, delete_saves_command

class ModService():
  def __init__(self):
    self.mod_client = ModClient(response_handler=JsonResponseHandler)
    self.ecs_client = EcsClient()
    self.ssh = SshService()

  async def get_releases(self, version, *mod_names):
    releases = []
    for mod in mod_names:
      try:
        mod_info = self.mod_client.get_mod(mod)
        release = get_release(mod_info, version)
        releases.append(release)
      except Exception as e:
        if hasattr(e, 'status_code') and e.status_code == 404:
          raise InvalidOperationException(f'Mod `{mod}` not found')
        else:
          raise
    return releases

  async def install_releases(self, name, ip, releases):
    try:
      await self.ecs_client.set_desired_count(name, 0)
      commands = [download_command(release) for release in releases]
      commands.append(delete_saves_command())
      self.ssh.exec(ip, commands)
    finally:
      await self.ecs_client.set_desired_count(name, 1)