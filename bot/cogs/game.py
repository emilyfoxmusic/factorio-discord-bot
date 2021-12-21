import io
import discord
from discord.ext import commands
from ..services import (game_service, inactivity_service, status_service,
                        channel_mapping_service, logs_service, player_service, ip_service)
from ..services.status_service import Status
from ..helpers import game_mapping_helper
from ..utilities import random_string
from .roles import FACTORIO_CATEGORY

STATUSES_TO_MESSAGES = {
    Status.CREATING: 'The game is being created as we speak :baby:',
    Status.RUNNING: 'The game is running! Go make some factories :tada:',
    Status.STOPPED: 'The game is currently stopped. Use `!start` to play! :factory_worker:',
    Status.STARTING: 'The game is starting up... get hyped :partying_face:',
    Status.STOPPING: 'The game is shutting down... see you again soon! :cry:',
    Status.DELETING: 'The game is being deleted RIP :skull_crossbones:',
}


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.confirmation_phrases = {}

    @commands.command(help='Get status of the game')
    async def status(self, ctx):
        game = await game_mapping_helper.game_from_context(ctx, self.bot)
        if game is not None:
            status = await status_service.get_status(game)
            message_for_status = STATUSES_TO_MESSAGES.get(status)
            if message_for_status is not None:
                await ctx.send(message_for_status)
            else:
                await ctx.send('Something is amiss - the stack state is not in an expected ' +
                               'state. Some debugging may be required... :detective:')

    @commands.command(help='Start the game server')
    async def start(self, ctx):
        game = await game_mapping_helper.game_from_context(ctx, self.bot)
        if game is not None:
            await ctx.send('Starting server...')
            await game_service.start(game)
            ip = await ip_service.get_ip(game)
            await ctx.send(f'Successfully started at `{ip}` :tada:')

    @commands.command(help='Stop the game server',
                      usage='[force]',
                      description="Stops the game server. Use the 'force' option " +
                      "(`!stop force`) if you'd like to stop the server even if the " +
                      "backup fails.")
    async def stop(self, ctx, *args):
        game = await game_mapping_helper.game_from_context(ctx, self.bot)
        force = len(args) > 0 and args[0].lower() == 'force'
        if game is not None:
            if force:
                await ctx.send('Stopping the server... :muscle:')
            else:
                await ctx.send('Taking a backup and stopping the server...')
            await game_service.stop(game, force)
            await ctx.send('Successfully stopped, goodbye :wave: ' +
                           '(Use `!list-backups` to get latest backup.)')

    @commands.command(help='Get the current IP address for the game')
    async def ip(self, ctx):
        game = await game_mapping_helper.game_from_context(ctx, self.bot)
        if game is not None:
            ip = await ip_service.get_ip(game)
            await ctx.send(f'Join at `{ip}` :construction:')


    @commands.command(help='Get the Factorio logs (for debugging mods)')
    async def debug(self, ctx, lines=20):
        game = await game_mapping_helper.game_from_context(ctx, self.bot)
        if game is not None:
            logs = await logs_service.get_factorio_logs_tail(game, lines)
            with io.StringIO(logs) as logs_file:
                await ctx.send("Debug trace:", file=discord.File(logs_file, "logs.txt"))

    @commands.command(help='Get the players for the game', usage='[all]')
    async def players(self, ctx, *args):
        game = await game_mapping_helper.game_from_context(ctx, self.bot)
        if game is not None:
            all_players = len(args) > 0 and args[0].lower() == 'all'
            if all_players:
                players = await player_service.get_all_players(game)
                message = 'This game has no players yet.' if players is None else players
                await ctx.send(message)
            else:
                players = await player_service.get_online_players(game)
                message = (
                    'There are no currently no players online.' if players is None else players)
                await ctx.send(message)

    @commands.command(help='Permanently delete the game',
                      description="Permanently delete the game. The game and associated " +
                      'discord channel will be permanently deleted. If you want to ' +
                      "host it again you'll have to set that up manually. **Make sure " +
                      "you have taken the appropriate backups.**")
    async def delete(self, ctx, confirmation_phrase=None):
        game = await game_mapping_helper.game_from_context(ctx, self.bot)
        if game is not None:
            if (confirmation_phrase is not None and
                    confirmation_phrase == self.confirmation_phrases.get(game)):
                del self.confirmation_phrases[game]
                await ctx.send(f'Deleting {game}')
                await game_service.delete_game(game)
                # We want to remove any channel associations with this game - the
                # easiest way to do that is just to validate the mappings again
                await channel_mapping_service.validate_mappings(self.bot)
                for guild in self.bot.guilds:
                    category = discord.utils.get(
                        guild.categories, name=FACTORIO_CATEGORY)
                    channel = discord.utils.get(category.channels, name=game)
                    if channel is not None:
                        await channel.delete()
            elif confirmation_phrase is None or self.confirmation_phrases.get(game) is None:
                self.confirmation_phrases[game] = random_string(10)
                await ctx.send(f':warning: :warning: :warning: Game "{game}" and associated ' +
                               'discord channel will be permanently deleted. If you want to ' +
                               "host it again you'll have to set that up manually. **Make sure " +
                               "you have taken the appropriate backups.** :warning: :warning: " +
                               ":warning: \nTo confirm the delete, use " +
                               f"`!delete {self.confirmation_phrases[game]}`")
            else:
                self.confirmation_phrases[game] = random_string(10)
                await ctx.send(':no_entry_sign: Confirmation phrase did not match - to confirm ' +
                               'the delete, use ' +
                               f'`!delete {self.confirmation_phrases[game]}`')
