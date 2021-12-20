from ..services import ip_service
from ..clients import ssh_client


async def get_factorio_logs_tail(game, lines):
    ip = await ip_service.get_ip(game)
    return ssh_client.execute_get(ip, f'tail -n {lines} /opt/factorio/factorio-current.log')
