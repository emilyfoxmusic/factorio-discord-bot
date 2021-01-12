from discord.ext import commands, tasks
from ..services import inactivityService, channelMappingService


class ChannelManagement(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
    await channelMappingService.init_channel_table()
    await channelMappingService.validate_mappings(self.bot)

  @commands.Cog.listener()
  async def on_guild_channel_delete(self, channel):
    await channelMappingService.remove_mappings(channel.guild.id, channel.id)

  @commands.Cog.listener()
  async def on_guild_remove(self, guild):
    await channelMappingService.remove_mappings(guild.id)
