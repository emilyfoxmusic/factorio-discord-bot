from discord.ext import commands
from ..services import channelMappingService, gameService, inactivityService
from ..helpers import statusHelper, gameMappingHelper


class Game(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(help='Get status of the game')
  async def status(self, ctx):
    game = await gameMappingHelper.game_from_context(ctx, self.bot)
    if game != None:
      status = await gameService.get_status(game)
      await ctx.send(statusHelper.message(status))

  @commands.command(help='Start the game server')
  async def start(self, ctx):
    game = await gameMappingHelper.game_from_context(ctx, self.bot)
    if game != None:
      await ctx.send(f'Starting server...')
      await gameService.start(game)
      ip = await gameService.get_ip(game)
      await ctx.send(f'Successfully started at `{ip}` :tada:')

  @commands.command(help='Stop the game server')
  async def stop(self, ctx):
    game = await gameMappingHelper.game_from_context(ctx, self.bot)
    if game != None:
      await ctx.send(f'Taking a backup and stopping server...')
      await gameService.stop(game)
      await ctx.send(f'Successfully stopped, goodbye :wave: (Use `!list-backups` to get latest backup.)')

  @commands.command(help='Get the IP address for the game (if running)')
  async def ip(self, ctx):
    game = await gameMappingHelper.game_from_context(ctx, self.bot)
    if game != None:
      ip = await gameService.get_ip(game)
      await ctx.send(f'Join at `{ip}` :construction:')
    
  @commands.command(help='Reset the server auto-shutdown timer', decription="When this command is invoked, the auto-shutdown resets and the game will stay up for another 30mins.", name="let-me-live")
  async def let_me_live(self, ctx):
    game = await gameMappingHelper.game_from_context(ctx, self.bot)
    if game != None:
      status = inactivityService.reset_idle_counter(game)
      await ctx.send("Ok, I'll stick around for a bit longer :dancer:")