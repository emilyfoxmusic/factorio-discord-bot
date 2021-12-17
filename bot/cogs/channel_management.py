from discord.ext import commands
from ..services import channel_mapping_service


class ChannelManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await channel_mapping_service.init_channel_table()
        await channel_mapping_service.validate_mappings(self.bot)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        await channel_mapping_service.remove_mappings(channel.guild.id, channel.id)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await channel_mapping_service.remove_mappings(guild.id)
