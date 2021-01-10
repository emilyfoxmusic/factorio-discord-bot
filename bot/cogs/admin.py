import re
import discord
from discord import ChannelType
from discord.ext import commands
from ..services import channelMappingService, gameService
from ..utilities import random_string
from .roles import FACTORIO_CATEGORY


name_pattern = re.compile("^[A-Za-z][A-Za-z0-9-]*$")

class Admin(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.confirmation_phrases = {}

  @commands.Cog.listener()
  async def on_ready(self):
    await channelMappingService.init_channel_table()

  @commands.command(help='Create a new game')
  async def new(self, ctx, name, version, *mods):
    if not name_pattern.match(name):
      await ctx.send(f'Name must only contain letters, numbers and -, and must start with a letter. :no_entry:')
      return
    await ctx.send(f'Creating new game: {name} :star2:')
    await gameService.create_game(name, version, *mods)
    for guild in self.bot.guilds:
      category = discord.utils.get(guild.categories, name=FACTORIO_CATEGORY)
      channel = await category.create_text_channel(name)
      await channelMappingService.set_channel_mapping(name, guild.id, channel.id)
    await ctx.send(f"Created {name}! Let's get this party started! :partying_face:")

  @commands.command(help='Delete a game')
  async def delete(self, ctx, name, confirmation_phrase=None):
    if confirmation_phrase != None and confirmation_phrase == self.confirmation_phrases.get(name):
      del self.confirmation_phrases[name]
      await ctx.send(f'Deleting {name}')
      await gameService.delete_game(name)
      await ctx.send(f'Your complimentary backup can be downloaded using `!list-backups {name}`')
      # We want to remove any channel associations with this game - the easiest way to do that
      # is just to validate the mappings again
      await channelMappingService.validate_mappings(self.bot)
      for guild in self.bot.guilds:
        category = discord.utils.get(guild.categories, name=FACTORIO_CATEGORY)
        channel = discord.utils.get(category.channels, name=name)
        if channel != None:
          await channel.delete()
      await ctx.send(f'Deleted {name}! :skull_crossbones:')
    elif confirmation_phrase == None or self.confirmation_phrases.get(name) == None:
      self.confirmation_phrases[name] = random_string(10)
      await ctx.send(f':warning: :warning: :warning: All data will be deleted - make sure to take a backup if you want to keep the game data! :warning: :warning: :warning: \n To confirm the delete, use `!delete {name} {self.confirmation_phrases[name]}`')
    else:
      self.confirmation_phrases[name] = random_string(10)
      await ctx.send(f':no_entry_sign: Confirmation phrase did not match - to confirm the delete, use `!delete {name} {self.confirmation_phrases[name]}`')

  @commands.command(name='set-game', help='Link the current channel to the specified game')
  async def set_game(self, ctx, name):
    if ctx.channel.type == ChannelType.private:
      await ctx.send("Sorry, I can't do that in DM.")
    elif await gameService.game_exists(name):
      await channelMappingService.set_channel_mapping(name, ctx.channel.guild.id, ctx.channel.id)
      await ctx.send(f'This channel will now control game `{name}` :control_knobs:')
    else:
      await ctx.send('Sorry, I did not recognise that game :confused:')

  @commands.command(help='List all games and their current statuses')
  async def list(self, ctx):
    games = await gameService.list_games()
    if (len(games) == 0):
      await ctx.send('There are no games at the moment. Create a new one with `!new`.')
      return
    game_summaries = [f'{game}: {status.name}' for (game, status) in games.items()]
    await ctx.send('Games: \n' + '\n'.join(game_summaries))