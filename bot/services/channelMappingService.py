import aiobotocore
import logging
from ..aws.channelMappingClient import ChannelMappingClient

class ChannelService():
  def __init__(self):
    self.channel_client = ChannelMappingClient()

  async def init_channel_table(self):
    if not await self.channel_client.check_table_exists():
      await self.channel_client.create_table()

  async def get_game_channel_mappings(self, name):
    await self.channel_client.get_mappings(name)

  async def set_channel_mapping(self, name, guild_id, channel_id):
    await self.channel_client.set_mapping(name, guild_id, channel_id)
