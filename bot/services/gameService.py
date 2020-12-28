import aiobotocore
import logging
from ..aws.stackClient import StackClient

class GameService():
  def __init__(self):
    self.stack_client = StackClient()

  async def create_game(self, name, version):
    await self.stack_client.create_stack(name, version)

  async def delete_game(self, name):
    await self.stack_client.delete_stack(name)

  async def list_games(self):
    return await self.stack_client.list_stacks()

  async def game_exists(self, name):
    game_names = map(lambda stack: stack['StackName'], await self.list_games())
    return name in game_names
