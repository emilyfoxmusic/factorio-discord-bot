from ..services import ip_service
from ..clients import ssh_client, ecs_client
from ..helpers.env import getenv


FACTORIO_USERNAME = getenv('FACTORIO_USERNAME')
FACTORIO_TOKEN = getenv('FACTORIO_TOKEN')


async def set_default_settings(game):
    ip = await ip_service.get_ip(game)
    ssh_client.execute(
        ip,
        'sudo yum install jq -y',
        'sudo chmod 666 /opt/factorio/config/server-settings.json',
        set_string('.name', game),
        set_string('.description', ''),
        set_false('.visibility.public'),
        set_false('.visibility.lan'),
        set_string('.username', FACTORIO_USERNAME),
        set_string('.token', FACTORIO_TOKEN),
        # we need this for our backup system to work as we always copy across the first save
        set_number('.autosave_slots', 1)
    )
    await ecs_client.restart_service(game)


def set_false(path):
    return (f"cat <<< $(jq '{path} = false' /opt/factorio/config/server-settings.json)" +
            " > /opt/factorio/config/server-settings.json")


def set_string(path, value):
    return (f'cat <<< $(jq \'{path} = "{value}"\' /opt/factorio/config/server-settings.json) ' +
            '> /opt/factorio/config/server-settings.json')


def set_number(path, value):
    return (f"cat <<< $(jq '{path} = {value}' /opt/factorio/config/server-settings.json) " +
            "> /opt/factorio/config/server-settings.json")