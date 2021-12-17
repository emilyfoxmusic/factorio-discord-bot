from discord.ext import commands, tasks
from ..services import inactivity_service


class AutoShutdown(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.handle_auto_shutdown.start()

    @tasks.loop(minutes=15)
    async def handle_auto_shutdown(self):
        await inactivity_service.auto_shutdown_loop(self.bot)
