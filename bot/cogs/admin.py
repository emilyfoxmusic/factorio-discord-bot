import logging
from discord.ext import commands
from ..services.channelMappingService import ChannelService
from ..services.gameService import GameService

class Admin(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.channels = ChannelService()
    self.games = GameService()

  @commands.Cog.listener()
  async def on_ready(self):
    await self.channels.init_channel_table()

  @commands.command(help='Create a new game', usage='<name> [version]')
  @commands.cooldown(1, 10)
  async def new(self, ctx, name, *args):
    version = args[0] if len(args) > 0 else 'latest'
    await ctx.send(f'Creating new game: {name} :star2:')
    await self.games.try_create_game(name, version)
    await ctx.send(f'Created {name}! Assign a channel with `!set-channel` and use `!start` to get the party started :partying_face:')

  @commands.command(help='Delete a game')
  @commands.cooldown(1, 10)
  async def delete(self, ctx, name):
    await ctx.send(f'Deleting {name}')
    await self.games.try_delete_game(name)
    await ctx.send(f'Deleted {name}! :skull_crossbones:')

  @commands.command(help='List all active games')
  @commands.cooldown(1, 5)
  async def list(self, ctx):
    stacks = await self.games.list_games()
    if (len(stacks) == 0):
      await ctx.send('There are no games at the moment. Create a new one with `!new`.')
      return
    await ctx.send('Active games: \n' + '\n'.join(stacks))

  @commands.command(name="set-game", help='Link the current channel to the specified game')
  async def set_game(self, ctx, name):
    if await self.games.game_exists(name):
      await self.channels.set_channel_mapping(name, ctx.channel.guild.id, ctx.channel.id)
      await ctx.send(f'This channel will now control game `{name}` :tada:')
    else:
      await ctx.send('Sorry, I did not recognise that game :confused:')
