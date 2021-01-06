from discord.ext import commands, tasks
from ..services import backupService


class Backups(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
    await backupService.init_backup_bucket()

  @commands.command(help='Take a backup of the game and post a download link')
  async def backup(self, ctx, game):
    url = await backupService.backup(game)
    await ctx.send(f'Backup created, download at {url} :safety_vest:')