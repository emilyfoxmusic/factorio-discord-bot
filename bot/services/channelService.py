import aiobotocore
import logging
from ..aws.channels import Channels

class ChannelService():
  def __init__(self):
    self.channels = Channels()

  async def init_channel_table(self):
    if not await self.channels.check_table_exists():
      await self.channels.create_table()

  async def get_game_mappings(self, name):
    await self.channels.get_mappings(name)

  async def set_channel_mapping(self, name, guild_id, channel_id):
    await self.channels.set_mapping(name, guild_id, channel_id)

