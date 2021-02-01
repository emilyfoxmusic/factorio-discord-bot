import discord
from ..helpers.env import getenv
from ..clients import s3Client, sshClient
from ..services import ipService, rconService
from ..utilities import random_string


REGION = getenv('AWS_DEFAULT_REGION')
AWS_ACCESS_KEY_ID = getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = getenv('AWS_SECRET_ACCESS_KEY')
BUCKET_BASE = 'factorio-backups'

bucket_name = None

async def init_backup_bucket():
  global bucket_name
  buckets = await s3Client.get_buckets()
  bucket_name = discord.utils.find(lambda b: b.startswith(BUCKET_BASE), map(lambda b: b['Name'], buckets))
  if bucket_name == None:
    bucket_name = f'{BUCKET_BASE}-{random_string(8).lower()}'
    await s3Client.create_bucket(bucket_name)

async def backup(game):
  rcon_client = await rconService.get_rcon_client(game)
  rcon_client.save()
  game_time = rcon_client.game_time().replace(' ', '')
  ip = await ipService.get_ip(game)
  sshClient.exec(ip, f'docker run -v /opt/factorio/saves:/saves --env AWS_ACCESS_KEY_ID={AWS_ACCESS_KEY_ID} --env AWS_SECRET_ACCESS_KEY={AWS_SECRET_ACCESS_KEY} --rm amazon/aws-cli s3 cp /saves/_autosave1.zip s3://{bucket_name}/{game}/{game_time}.zip --acl public-read')

async def list_backups(game):
  game_backups = await s3Client.list_objects(bucket_name, game)
  return list(map(lambda file: {
    'url': build_link(file['Key']),
    'title': file['Key'].replace(f'{game}/', ''),
    'taken_at': file['LastModified']
  }, game_backups))

def build_link(key):
  return f'https://{bucket_name}.s3.{REGION}.amazonaws.com/{key}'