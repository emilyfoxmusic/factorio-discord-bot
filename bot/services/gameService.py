import aiobotocore
import logging
import os
from ..aws.stackClient import StackClient
from ..helpers.single import single
from ..helpers.statusHelper import get_status, Status
from ..exceptions.invalidOperationException import InvalidOperationException
from .modService import ModService
from .versionService import VersionService

class GameService():
  def __init__(self):
    self.stack_client = StackClient()
    self.mod_service = ModService()
    self.version_service = VersionService()

  async def try_create_game(self, name, version, *mods):
    if await self.game_exists(name):
      raise InvalidOperationException('Game already exists')

    # We don't use the parsed version if there are no mods, but we still 
    # want to run it through to make sure that what the user entered is a
    # *syntactically* valid version
    parsed_version = await self.version_service.get_version(version)

    if (len(mods)) == 0:
      await self.stack_client.create_stack(name, version)
      return

    # We must check the mods *before* creating the stack in case they are invalid
    mods_releases = await self.mod_service.get_releases(parsed_version, *mods)
    await self.stack_client.create_stack(name, version)
    ip = await self.try_get_ip(name)
    await self.mod_service.install_releases(name, ip, mods_releases)

  async def try_delete_game(self, name):
    if (await self.game_exists(name)):
      await self.stack_client.delete_stack(name)
    else:
      raise InvalidOperationException('Game not found')

  async def list_games(self):
    stacks = await self.stack_client.list_stacks()
    return list(map(lambda stack: stack['StackName'], stacks))

  async def game_exists(self, name):
    return name in await self.list_games()

  async def try_get_status(self, name):
    if (not await self.game_exists(name)):
      raise InvalidOperationException('Game not found')
    stack = await self.stack_client.stack_details(name)
    server_state_param = single(lambda parameter: parameter['ParameterKey'] == 'ServerState', stack['Parameters'])
    return get_status(stack['StackStatus'], server_state_param['ParameterValue']) 

  async def try_start(self, name):
    status = await self.try_get_status(name)
    if status == Status.STOPPED or status == Status.UNRECOGNISED:
      await self.stack_client.update_stack(name, 'Running')
    elif status == Status.STARTING or status == Status.RUNNING:
      raise InvalidOperationException('Server is already running/starting')
    else:
      raise InvalidOperationException('Please wait - another operation is in progress')

  async def try_stop(self, name):
    status = await self.try_get_status(name)
    if status == Status.RUNNING or status == Status.UNRECOGNISED:
      await self.stack_client.update_stack(name, 'Stopped')
    elif status == Status.STOPPING or status == Status.STOPPED:
      raise InvalidOperationException('Server is already stopped/stopping')
    else:
      raise InvalidOperationException('Please wait - another operation is in progress')

  async def try_get_ip(self, name):
    status = await self.try_get_status(name)
    if status == Status.RUNNING:
      instance = await self.stack_client.get_ec2_instance(name)
      return instance['PublicIpAddress']
    else:
      raise InvalidOperationException('Server is not running (yet?)')
