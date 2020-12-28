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
    return await self.channels.get_game(ctx.channel.guild.id, ctx.channel.id)

  @commands.command(help='Get status of the game')
  async def status(self, ctx):
    name = await self.game_from_context(ctx)
    status = await self.games.try_get_status(name)
    await ctx.send(status_message(status))

  @commands.command(help='Start the game server')
  async def start(self, ctx):
    name = await self.game_from_context(ctx)
    await self.games.try_start(name)
    await ctx.send('Successfully started :tada:')

  @commands.command(help='Stop the game server')
  async def stop(self, ctx):
    name = await self.game_from_context(ctx)
    await self.games.try_stop(name)
    await ctx.send('Successfully stopped, goodbye :wave:')
