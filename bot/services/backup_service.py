import discord
from ..helpers.env import getenv
from ..clients import s3_client, ssh_client
from ..services import ip_service, rcon_service
from ..utilities import random_string


REGION = getenv('AWS_DEFAULT_REGION')
AWS_ACCESS_KEY_ID = getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = getenv('AWS_SECRET_ACCESS_KEY')
BUCKET_BASE = 'factorio-backups'

BUCKET_NAME = None


async def init_backup_bucket():
    global BUCKET_NAME  # pylint: disable=global-statement
    buckets = await s3_client.get_buckets()
    BUCKET_NAME = discord.utils.find(lambda b: b.startswith(
        BUCKET_BASE), map(lambda b: b['Name'], buckets))
    if BUCKET_NAME is None:
        BUCKET_NAME = f'{BUCKET_BASE}-{random_string(8).lower()}'
        await s3_client.create_bucket(BUCKET_NAME)


async def backup(game):
    rcon_client = await rcon_service.get_rcon_client(game)
    rcon_client.save()
    game_time = rcon_client.game_time().replace(' ', '')
    ip = await ip_service.get_ip(game)
    ssh_client.execute(
        ip,
        'docker run -v /opt/factorio/saves:/saves ' +
        f'--env AWS_ACCESS_KEY_ID={AWS_ACCESS_KEY_ID} ' +
        f'--env AWS_SECRET_ACCESS_KEY={AWS_SECRET_ACCESS_KEY} ' +
        '--rm amazon/aws-cli ' +
        's3 cp /saves/$(ls /opt/factorio/saves/ -t | head -n1) ' +
        f's3://{BUCKET_NAME}/{game}/{game_time}.zip --acl public-read')


async def list_backups(game):
    game_backups = await s3_client.list_objects(BUCKET_NAME, game)
    return list(map(lambda file: {
        'url': build_link(file['Key']),
        'title': file['Key'].replace(f'{game}/', ''),
        'taken_at': file['LastModified']
    }, game_backups))


def build_link(key):
    return f'https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/{key}'
