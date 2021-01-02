import os
from packaging.version import parse
from ..clients import modClient, ecsClient, sshClient, factorioClient
from ..services import ipService
from ..exceptions import InvalidOperationException


FACTORIO_USERNAME = os.getenv('FACTORIO_USERNAME')
FACTORIO_TOKEN = os.getenv('FACTORIO_TOKEN')

async def get_releases(version, *mod_names):
  absolute_version = get_absolute_version(version)
  releases = []
  for mod in mod_names:
    try:
      mod_info = modClient.client.get_mod(mod)
      releases.append(pick_release(mod_info, absolute_version))
    except Exception as e:
      if hasattr(e, 'status_code') and e.status_code == 404:
        raise InvalidOperationException(f'Mod `{mod}` not found')
      else:
        raise
  return releases

async def install_releases(name, releases):
  ip = ipService.get_ip(name)
  try:
    await ecsClient.set_desired_count(name, 0)
    commands = [download_command(release) for release in releases]
    commands.append('sudo rm /opt/factorio/saves/*')
    sshClient.exec(ip, *commands)
  finally:
    await ecsClient.set_desired_count(name, 1)

def pick_release(mod_info, version):
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

def get_absolute_version(version_param):
  if version_param == 'latest' or version_param == 'stable':
    latest_releases = factorioClient.client.get_latest_releases()
    absolute_version = latest_releases['experimental' if version_param == 'latest' else 'stable']['headless']
    return parse(absolute_version)
  return parse(version_param)
