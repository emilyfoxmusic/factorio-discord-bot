import json
import re
from ..services import ip_service
from ..clients import ssh_client, ecs_client
from ..helpers.env import getenv
from ..exceptions import InvalidOperationException

FACTORIO_USERNAME = getenv('FACTORIO_USERNAME')
FACTORIO_TOKEN = getenv('FACTORIO_TOKEN')

player_pattern = re.compile("^[A-Za-z0-9.-]+$")

SERVER_CONFIG_FILE = '/opt/factorio/config/server-settings.json'
ADMIN_LIST_FILE = '/opt/factorio/config/server-adminlist.json'

INSTALL_JQ = 'sudo yum install jq -y'


async def set_default_config(game):
    ip = await ip_service.get_ip(game)
    ssh_client.execute(
        ip,
        INSTALL_JQ,
        f'sudo chmod 666 {SERVER_CONFIG_FILE}',
        write_setting_string('.name', game),
        write_setting_string('.description', ''),
        write_setting_false('.visibility.public'),
        write_setting_false('.visibility.lan'),
        write_setting_string('.username', FACTORIO_USERNAME),
        write_setting_string('.token', FACTORIO_TOKEN),
        # Saving every 8 minutes and using 2 slots means that:
        # 1) when saving there is always another backup so if the server
        # dies in the middle of saving we don't lose everything
        # 2) 8 minutes seems like a decent balance between risk of
        # losing work vs. interruption while the server saves
        write_setting_number('.autosave_slots', 2),
        write_setting_number('.autosave_interval', 8),
        # Initialise adminlist file
        f'sudo sh -c \'echo "[]" > {ADMIN_LIST_FILE}\'',
        f'sudo chmod 666 {ADMIN_LIST_FILE}'
    )
    await ecs_client.restart_service(game)


async def add_admins(game, players):
    await modify_admins(
        game,
        players,
        lambda existing_admins: lambda player: player in existing_admins,
        'At least one of those players is already an admin',
        '+')


async def remove_admins(game, players):
    await modify_admins(
        game,
        players,
        lambda existing_admins: lambda player: player not in existing_admins,
        'At least one of those players is not currently an admin',
        '-')


async def modify_admins(game, players, get_invalid_players, invalid_message, jq_operator):
    if any(not player_pattern.match(player) for player in players):
        raise InvalidOperationException(
            'Player names must only contain letters, numbers, full-stops and hyphens')
    ip = await ip_service.get_ip(game)
    existing_admins = await get_admins(game)
    invalid_players = list(
        filter(get_invalid_players(existing_admins), players))
    if any(invalid_players):
        raise InvalidOperationException(
            f'{invalid_message}: {", ".join(invalid_players)}.')
    json_players = json.dumps(players)
    ssh_client.execute(
        ip,
        INSTALL_JQ,
        write_file(ADMIN_LIST_FILE, f'jq \'. {jq_operator} {json_players}\''))


async def get_admins(game):
    ip = await ip_service.get_ip(game)
    ssh_client.execute(ip, INSTALL_JQ)
    return ssh_client.execute_get(ip, f'jq \'. | join(",")\' -r {ADMIN_LIST_FILE}').split(',')


def write_file(file, expression):
    return f"cat <<< $({expression} {file}) > {file}"


def write_setting_false(path):
    return write_file(SERVER_CONFIG_FILE, f"jq '{path} = false'")


def write_setting_string(path, value):
    return write_file(SERVER_CONFIG_FILE, f'jq \'{path} = "{value}"\'')


def write_setting_number(path, value):
    return write_file(SERVER_CONFIG_FILE, f"jq '{path} = {value}'")
