from apiclient import JsonResponseHandler
from packaging.version import parse
from ..api.factorioClient import FactorioClient

class VersionService():
  def __init__(self):
    self.api = FactorioClient(response_handler=JsonResponseHandler)

  async def get_version(self, version_param):
    if version_param == 'latest' or version_param == 'stable':
      latest_releases = self.api.get_latest_releases()
      absolute_version = latest_releases['experimental' if version_param == 'latest' else 'stable']['headless']
      return parse(absolute_version)
    return parse(version_param)
