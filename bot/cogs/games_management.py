import re
import discord
from discord import ChannelType
from discord.ext import commands
from ..services import channel_mapping_service, game_service, ip_service, status_service
from .roles import FACTORIO_CATEGORY

name_pattern = re.compile("^[A-Za-z][A-Za-z0-9-]*$")


class GamesManagement(commands.Cog, name="Managing Games"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='Create a new game',
                      description="This will create a new game with the mods that you specify. " +
                      "Version must be a valid tag for the factorio tools docker container: " +
                      "https://hub.docker.com/r/factoriotools/factorio/. Generally you will want" +
                      " to use 'latest' or 'stable'.\n\ne.g. `!new my-game latest Krastorio2 " +
                      "clock`")
    async def new(self, ctx, name, version, *mods):
        if not name_pattern.match(name):
            await ctx.send('Name must only contain letters, numbers and -, and must start with a ' +
                           'letter. :no_entry:')
            return
        await ctx.send(f'Creating new game: {name} :star2:')
        await game_service.create_game(name, version, *mods)
        for guild in self.bot.guilds:
            category = discord.utils.get(
                guild.categories, name=FACTORIO_CATEGORY)
            channel = await category.create_text_channel(name)
            await channel_mapping_service.set_channel_mapping(name, guild.id, channel.id)
        ip = await ip_service.get_ip(name)
        if await game_service.passes_healthcheck(name):
            await ctx.send(f"Created {name} - now running at `{ip}`! Let's get this party " +
                           "started! :partying_face:")
        else:
            await ctx.send(f"Created {name} at `{ip}`. **However**, it looks " +
                           "like there's a problem because the game doesn't appear " +
                           "to be running. This is most likely due to incompatibility between " +
                           "mods. Use `!debug` to see the logs. :thermometer_face:")

    @commands.command(name='set-game',
                      help='Link the current channel to the specified game',
                      description="You generally won't need this as text channels are " +
                      "automatically created for you, but you can use this to add extra " +
                      "channels for a game if you wish. (Note you'll need to invite the bot " +
                      "explicitly if the channel is not in the factorio servers category.)")
    async def set_game(self, ctx, name):
        if ctx.channel.type == ChannelType.private:
            await ctx.send("Sorry, I can't do that in DM.")
        elif await game_service.game_exists(name):
            await channel_mapping_service.set_channel_mapping(
                name,
                ctx.channel.guild.id,
                ctx.channel.id)
            await ctx.send(f'This channel will now control game `{name}` :control_knobs:')
        else:
            await ctx.send('Sorry, I did not recognise that game :confused:')

    @commands.command(help='List all games and their current statuses')
    async def list(self, ctx):
        games = await status_service.list_game_statuses()
        if len(games) == 0:
            await ctx.send('There are no games at the moment. Create a new one with `!new`.')
            return
        game_summaries = [f'{game}: {status.name}' for (
            game, status) in games.items()]
        await ctx.send('Games: \n' + '\n'.join(game_summaries))
