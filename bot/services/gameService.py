import logging
from ..exceptions import InvalidOperationException
from ..clients import stackClient, s3Client
from ..services import modService, ipService, backupService
from ..helpers import statusHelper
from ..utilities import single


async def create_game(name, version, *mods):
  if await game_exists(name):
    raise InvalidOperationException('Game already exists')
  # We must check the mods *before* creating the stack in case they are invalid
  # Note this also happens to check the version is syntactically correct, so it's
  # worth running even with no mods.
  mod_releases = await modService.get_releases(parsed_version, *mods)
  await stackClient.create_stack(name, version)
  if len(mod_releases) > 0:
    await modService.install_releases(name, mod_releases)

async def delete_game(name):
  if not await game_exists(name):
    raise InvalidOperationException('Game not found')
  if await get_status(name) == statusHelper.Status.DELETING:
    raise InvalidOperationException('Deletion already in progress')
  await backupService.backup(name)
  await stackClient.delete_stack(name)
  ipService.purge_ip(name)

async def get_status(name):
  stack = await stackClient.stack_details(name)
  return _status_from_stack(stack)

async def start(name):
  status = await get_status(name)
  if status == statusHelper.Status.STOPPED or status == statusHelper.Status.UNRECOGNISED:
    await stackClient.update_stack(name, 'Running')
  elif status == statusHelper.Status.STARTING or status == statusHelper.Status.RUNNING:
    raise InvalidOperationException('Server is already running/starting')
  else:
    raise InvalidOperationException('Please wait - another operation is in progress')

async def stop(name):
  status = await get_status(name)
  if status == statusHelper.Status.RUNNING or status == statusHelper.Status.UNRECOGNISED:
    await backupService.backup(name)
    await stackClient.update_stack(name, 'Stopped')
    ipService.purge_ip(name)
  elif status == statusHelper.Status.STOPPING or status == statusHelper.Status.STOPPED:
    raise InvalidOperationException('Server is already stopped/stopping')
  else:
    raise InvalidOperationException('Please wait - another operation is in progress')

async def get_ip(name):
  status = await get_status(name)
  if status == statusHelper.Status.RUNNING:
    return await ipService.get_ip(name)
  else:
    raise InvalidOperationException('Server is not running (yet?)')

async def list_games():
  stacks = await stackClient.list_stacks()
  return { stack['StackName']: _status_from_stack(stack) for stack in stacks }

async def game_exists(name):
  return name in await list_games()

def _status_from_stack(stack):
  server_state_param = single(lambda parameter: parameter['ParameterKey'] == 'ServerState', stack['Parameters'])
  return statusHelper.get_status(stack['StackStatus'], server_state_param['ParameterValue'])