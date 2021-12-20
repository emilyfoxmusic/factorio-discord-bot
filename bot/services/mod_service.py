from packaging.version import parse
from apiclient import exceptions
from ..clients import mod_client, ecs_client, ssh_client, factorio_client
from ..services import ip_service
from ..exceptions import InvalidOperationException
from ..helpers.env import getenv


FACTORIO_USERNAME = getenv('FACTORIO_USERNAME')
FACTORIO_TOKEN = getenv('FACTORIO_TOKEN')


async def get_releases(version, *mod_names):
    absolute_version = get_absolute_version(version)
    releases = []
    for mod in mod_names:
        try:
            mod_info = mod_client.client.get_mod(mod)
            releases.append(pick_release(mod_info, absolute_version))
        except exceptions.ClientError as error:
            if error.status_code == 404:
                raise InvalidOperationException(
                    f'Mod `{mod}` not found') from error
            raise
    return releases


async def install_releases(name, releases):
    ip = await ip_service.get_ip(name)
    try:
        await ecs_client.set_desired_count(name, 0)
        commands = [download_command(release) for release in releases]
        commands.append('sudo rm /opt/factorio/saves/*')
        ssh_client.execute(ip, *commands)
    finally:
        await ecs_client.set_desired_count(name, 1)


def pick_release(mod_info, version):
    releases = mod_info['releases']
    applicable_releases = list(filter(
        lambda release: parse(
            release['info_json']['factorio_version']) <= version,
        releases))
    if len(applicable_releases) == 0:
        name = mod_info['name']
        raise InvalidOperationException(
            f'No versions of {name} found for Factorio {version}')
    latest_applicable_release = max(
        applicable_releases,
        key=lambda release: parse(release['version']))
    return latest_applicable_release


def download_command(release):
    url = release['download_url']
    file_name = release['file_name']
    return ('sudo curl -L ' +
            f'"https://mods.factorio.com{url}' +
            f'?username={FACTORIO_USERNAME}&token={FACTORIO_TOKEN}" ' +
            f'--output /opt/factorio/mods/{file_name}')


VERSION_MAPPING = {
    'latest': 'experimental',
    'stable': 'stable'
}


def get_absolute_version(version_param):
    if version_param in VERSION_MAPPING:
        latest_releases = factorio_client.client.get_latest_releases()
        api_version = VERSION_MAPPING[version_param]
        if not api_version in latest_releases or not 'headless' in latest_releases[api_version]:
            raise InvalidOperationException(
                f'Version {version_param} is not currently available.')
        absolute_version = latest_releases[api_version]['headless']
        return parse(absolute_version)
    return parse(version_param)
