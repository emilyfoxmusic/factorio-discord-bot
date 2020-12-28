import aiobotocore
import logging
from ..aws.stackClient import StackClient
from ..helpers.single import single
from ..helpers.statusHelper import interpret_status

class GameService():
  def __init__(self):
    self.stack_client = StackClient()

  async def create_game(self, name, version):
    await self.stack_client.create_stack(name, version)

  async def delete_game(self, name):
    await self.stack_client.delete_stack(name)

  async def list_games(self):
    return await self.stack_client.list_stacks()

  async def get_game_by_name(self, name):
    filtered_games = list(filter(lambda stack: stack['StackName'] == name, await self.list_games()))
    return filtered_games[0] if len(filtered_games) > 0 else None

  async def game_exists(self, name):
    game = await self.get_game_by_name(name)
    return game != None

  async def get_status(self, name):
    stack = await self.stack_client.stack_details(name)
    server_state_param = single(lambda parameter: parameter['ParameterKey'] == 'ServerState', stack['Parameters'])
    return interpret_status(stack['StackStatus'], server_state_param['ParameterValue'])