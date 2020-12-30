import os
from packaging.version import parse
from ..exceptions.invalidOperationException import InvalidOperationException

FACTORIO_USERNAME = os.getenv('FACTORIO_USERNAME')
FACTORIO_TOKEN = os.getenv('FACTORIO_TOKEN')

def get_release(mod_info, version):
  releases = mod_info['releases']
  applicable_releases = list(filter(
    lambda release: parse(release['info_json']['factorio_version']) <= version,
    releases))
  if len(applicable_releases) == 0:
    name = mod_info['name']
    raise InvalidOperationException(f'No versions of {name} found for Factorio {version}')
  latest_applicable_release = max(
    applicable_releases,
    key=lambda release: parse(release['version']))
  return latest_applicable_release

def download_command(release):
  url = release['download_url']
  file_name = release['file_name']
  return f'sudo curl -L "https://mods.factorio.com{url}?username={FACTORIO_USERNAME}&token={FACTORIO_TOKEN}" --output /opt/factorio/mods/{file_name}'

def delete_saves_command():
  return 'sudo rm /opt/factorio/saves/*'