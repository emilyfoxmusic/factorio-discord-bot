from discord.ext import commands
from ..services import channelMappingService, gameService, inactivityService
from ..helpers import statusHelper


class Game(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  async def game_from_context(self, ctx):
    game = await channelMappingService.get_game(ctx.channel.guild.id, ctx.channel.id)
    if game == None:
      await ctx.send('This channel does not have an associated game - use `!set-channel` to assign a game to this channel.')
    return game

  @commands.command(help='Get status of the game')
  async def status(self, ctx):
    game = await self.game_from_context(ctx)
    if game != None:
      status = await gameService.get_status(game)
      await ctx.send(statusHelper.message(status))

  @commands.command(help='Start the game server')
  async def start(self, ctx):
    game = await self.game_from_context(ctx)
    if game != None:
      await ctx.send(f'Starting server...')
      await gameService.start(game)
      ip = await gameService.get_ip(game)
      await ctx.send(f'Successfully started at `{ip}` :tada:')

  @commands.command(help='Stop the game server')
  async def stop(self, ctx):
    game = await self.game_from_context(ctx)
    if game != None:
      await ctx.send(f'Stopping server (taking a backup first)...')
      backup_url = await gameService.stop(game)
      await ctx.send(f'Successfully stopped, goodbye :wave: \n (Your backup can be found at {backup_url} :safety_vest:)')

  @commands.command(help='Get the IP address associated with the game (if running)')
  async def ip(self, ctx):
    game = await self.game_from_context(ctx)
    if game != None:
      ip = await gameService.get_ip(game)
      await ctx.send(f'Join at `{ip}` :construction:')
    
  @commands.command(help='Reset the server auto-shutdown timer for the game')
  async def letmelive(self, ctx):
    game = await self.game_from_context(ctx)
    if game != None:
      status = inactivityService.reset_idle_counter(game)
      await ctx.send("Ok, I'll stick around for a bit longer :dancer:")