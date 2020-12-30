from apiclient import JsonResponseHandler
from .versionService import VersionService
from ..api.modClient import ModClient
from ..helpers.modHelper import download_link
from ..exceptions.invalidOperationException import InvalidOperationException

class ModService():
  def __init__(self):
    self.mod_client = ModClient(response_handler=JsonResponseHandler)
    self.version_service = VersionService()

  async def get_download_urls(self, version, *mod_names):
    parsed_version = await self.version_service.get_version(version)
    mod_download_urls = []
    for mod in mod_names:
      try:
        mod_info = self.mod_client.get_mod(mod)
        mod_download_urls.append(download_link(mod_info, parsed_version))
      except Exception as e:
        if hasattr(e, 'status_code') and e.status_code == 404:
          raise InvalidOperationException(f'Mod `{mod}` not found')
        else:
          raise
    return mod_download_urls
