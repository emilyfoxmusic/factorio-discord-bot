import aiobotocore
import logging
from ..aws.stackClient import StackClient
from ..helpers.single import single
from ..helpers.statusHelper import get_status, Status
from ..exceptions.invalidOperationException import InvalidOperationException

class GameService():
  def __init__(self):
    self.stack_client = StackClient()

  async def try_create_game(self, name, version):
    if (not await self.game_exists(name)):
      await self.stack_client.create_stack(name, version)
    else:
      raise InvalidOperationException('Game already exists')

  async def try_delete_game(self, name):
    if (await self.game_exists(name)):
      await self.stack_client.delete_stack(name)
    else:
      raise InvalidOperationException('Game not found')

  async def list_games(self):
    return await self.stack_client.list_stacks()

  async def get_game_by_name(self, name):
    filtered_games = list(filter(lambda stack: stack['StackName'] == name, await self.list_games()))
    return filtered_games[0] if len(filtered_games) > 0 else None

  async def game_exists(self, name):
    game = await self.get_game_by_name(name)
    return game != None

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