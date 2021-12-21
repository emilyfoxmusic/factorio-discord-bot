from discord.ext import commands, tasks
from ..services import inactivity_service
from ..helpers import game_mapping_helper


class AutoShutdown(commands.Cog, name='Auto-Shutdown'):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.handle_auto_shutdown.start()

    @tasks.loop(minutes=15)
    async def handle_auto_shutdown(self):
        await inactivity_service.auto_shutdown_loop(self.bot)

    @commands.command(help='Reset the server auto-shutdown timer',
                      decription="When this command is invoked, the auto-shutdown " +
                      "resets and the game will stay up for another 30mins.",
                      name="let-me-live")
    async def let_me_live(self, ctx):
        game = await game_mapping_helper.game_from_context(ctx, self.bot)
        if game is not None:
            inactivity_service.reset_idle_counter(game)
            await ctx.send("Ok, I'll stick around for a bit longer :dancer:")
