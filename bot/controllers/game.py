import logging
from discord.ext import commands
from ..services.channelMappingService import ChannelService
from ..services.gameService import GameService

class Game(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.channels = ChannelService()
    self.games = GameService()

  @commands.command(help='Gets status of the game')
  async def status(self, ctx):
    try:
      name = await self.channels.get_game(ctx.channel.guild.id, ctx.channel.id)
      status = await self.games.get_status(name)
      await ctx.send(status)
    except:
      await ctx.send('ERROR :fire:')
