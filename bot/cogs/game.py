import logging
from discord.ext import commands
from ..services.channelMappingService import ChannelService
from ..services.gameService import GameService
from ..helpers.statusHelper import status_message

class Game(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.channels = ChannelService()
    self.games = GameService()

  async def game_from_context(self, ctx):
    name = await self.channels.get_game(ctx.channel.guild.id, ctx.channel.id)
    if name == None:
      await ctx.send('This channel does not have an associated game - use `!set-channel` to assign a game to this channel.')
    return name

  @commands.command(help='Get status of the game')
  @commands.cooldown(1, 5)
  async def status(self, ctx):
    name = await self.game_from_context(ctx)
    if name != None:
      status = await self.games.try_get_status(name)
      await ctx.send(status_message(status))

  @commands.command(help='Start the game server')
  @commands.cooldown(1, 10)
  async def start(self, ctx):
    name = await self.game_from_context(ctx)
    if name != None:
      await ctx.send(f'Starting server...')
      await self.games.try_start(name)
      ip = await self.games.try_get_ip(name)
      await ctx.send(f'Successfully started at `{ip}` :tada:')

  @commands.command(help='Stop the game server')
  @commands.cooldown(1, 10)
  async def stop(self, ctx):
    name = await self.game_from_context(ctx)
    if name != None:
      await ctx.send(f'Stopping server...')
      await self.games.try_stop(name)
      await ctx.send('Successfully stopped, goodbye :wave:')

  @commands.command(help='Get the IP address associated with the game (if running)')
  @commands.cooldown(1, 10)
  async def ip(self, ctx):
    name = await self.game_from_context(ctx)
    if name != None:
      ip = await self.games.try_get_ip(name)
      await ctx.send(f'Join at `{ip}` :construction:')