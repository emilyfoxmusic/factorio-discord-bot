from packaging.version import parse
from ..exceptions.invalidOperationException import InvalidOperationException

def download_link(mod_info, version):
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
  return latest_applicable_release['download_url']