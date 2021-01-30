from discord.ext import commands, tasks
from ..services import inactivityService, channelMappingService


class AutoShutdown(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
    self.handle_auto_shutdown.start()

  @tasks.loop(minutes=15)
  async def handle_auto_shutdown(self):
    await inactivityService.auto_shutdown_loop(self.bot)