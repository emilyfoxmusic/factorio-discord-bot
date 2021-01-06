import discord
from discord.ext import commands, tasks
from ..services import backupService, gameService
from ..helpers import gameMappingHelper, statusHelper


class Backups(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
    await backupService.init_backup_bucket()

  @commands.command(help='Take a backup of the game associated with this channel and post a download link')
  async def backup(self, ctx):
    game = await gameMappingHelper.game_from_context(ctx, self.bot)
    if game != None:
      await ctx.send(f'Taking a backup now...')
      status = await gameService.get_status(game)
      if status == statusHelper.Status.RUNNING:
        await backupService.backup(game)
        await self.list_backups(ctx, 1)
      else:
        await ctx.send(f'Backups can only be taken when the server is running :no_entry_sign:')

  @commands.command(name='list-backups', help='Get the latest backups for the game associated with this channel')
  async def list_backups(self, ctx, number=3, *args):
    game = args[0] if len(args) > 0 else await gameMappingHelper.game_from_context(ctx, self.bot)
    if game != None:
      backups = await backupService.list_backups(game)
      backups.sort(key=lambda backup: backup['taken_at'], reverse=True)
      backups = backups[:number]
      if len(backups) == 0:
        await ctx.send(f"No backups found for '{game}' :skull:")
      for backup in backups:
        taken_at = backup['taken_at']
        embedded_link = discord.Embed(title=backup['title'], url=backup['url'], description=f'Backup taken: {taken_at:%d, %b %Y %H:%M}.')
        await ctx.send(embed=embedded_link)