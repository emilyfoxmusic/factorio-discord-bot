import re
import discord
from discord import ChannelType
from discord.ext import commands
from ..services import channelMappingService, gameService, ipService
from ..utilities import random_string
from .roles import FACTORIO_CATEGORY


name_pattern = re.compile("^[A-Za-z][A-Za-z0-9-]*$")

class Admin(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.confirmation_phrases = {}

  @commands.command(help='Create a new game', description="This will create a new game with the mods that you specify. Version must be a valid tag for the factorio tools docker container: https://hub.docker.com/r/factoriotools/factorio/. Generally you will want to use 'latest' or 'stable'.\n\ne.g. `!new my-game latest Krastorio2 clock`")
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
    ip = await ipService.get_ip(name)
    await ctx.send(f"Created {name} - now running at `{ip}`! Let's get this party started! :partying_face:")

  @commands.command(help='Delete a game', description="This will permanently delete the game (a backup will be taken first).")
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
      await ctx.send(f":warning: :warning: :warning: The game and associated discord channel will be permanetly deleted. If you want to host it again you'll have to set that up manually - I cannot help you with that (although I will provide you with the backup). :warning: :warning: :warning: \n To confirm the delete, use `!delete {name} {self.confirmation_phrases[name]}`")
    else:
      self.confirmation_phrases[name] = random_string(10)
      await ctx.send(f':no_entry_sign: Confirmation phrase did not match - to confirm the delete, use `!delete {name} {self.confirmation_phrases[name]}`')

  @commands.command(name='set-game', help='Link the current channel to the specified game', description="You generally won't need this as text channels are automatically created for you, but you can use this to add extra channels for a game if you wish. (Note you'll need to invite the bot explicitly if the channel is not in the factorio servers category.)")
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