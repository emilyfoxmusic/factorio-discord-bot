import io
import discord
from discord.ext import commands
from ..services import game_service, inactivity_service, channel_mapping_service, logs_service
from ..helpers import status_helper, game_mapping_helper
from ..utilities import random_string
from .roles import FACTORIO_CATEGORY


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.confirmation_phrases = {}

    @commands.command(help='Get status of the game')
    async def status(self, ctx):
        game = await game_mapping_helper.game_from_context(ctx, self.bot)
        if game is not None:
            status = await game_service.get_status(game)
            await ctx.send(status_helper.message(status))

    @commands.command(help='Start the game server')
    async def start(self, ctx):
        game = await game_mapping_helper.game_from_context(ctx, self.bot)
        if game is not None:
            await ctx.send('Starting server...')
            await game_service.start(game)
            ip = await game_service.get_ip(game)
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
                await ctx.send('Stopping the server, even if the backup fails... :muscle:')
            else:
                await ctx.send('Taking a backup and stopping the server...')
            await game_service.stop(game, force)
            await ctx.send('Successfully stopped, goodbye :wave: ' +
                           '(Use `!list-backups` to get latest backup.)')

    @commands.command(help='Get the IP address for the game (if running)')
    async def ip(self, ctx):
        game = await game_mapping_helper.game_from_context(ctx, self.bot)
        if game is not None:
            ip = await game_service.get_ip(game)
            await ctx.send(f'Join at `{ip}` :construction:')

    @commands.command(help='Reset the server auto-shutdown timer',
                      decription="When this command is invoked, the auto-shutdown " +
                      "resets and the game will stay up for another 30mins.",
                      name="let-me-live")
    async def let_me_live(self, ctx):
        game = await game_mapping_helper.game_from_context(ctx, self.bot)
        if game is not None:
            inactivity_service.reset_idle_counter(game)
            await ctx.send("Ok, I'll stick around for a bit longer :dancer:")

    @commands.command(help='Get the Factorio logs (for debugging mods)')
    async def debug(self, ctx, lines=20):
        game = await game_mapping_helper.game_from_context(ctx, self.bot)
        if game is not None:
            logs = await logs_service.get_factorio_logs_tail(game, lines)
            with io.StringIO(logs) as logs_file:
                await ctx.send("Debug trace:", file=discord.File(logs_file, "logs.txt"))

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
