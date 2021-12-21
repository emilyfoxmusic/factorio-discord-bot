from discord.ext import commands
from ..services import status_service, config_service
from ..helpers import game_mapping_helper
from ..clients import ecs_client


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='Get the current admins')
    async def admins(self, ctx):
        game = await game_mapping_helper.game_from_context(ctx, self.bot)
        if game is not None:
            current_admins = await config_service.get_admins(game)
            if any(current_admins):
                await ctx.send(f'Current admins are: {", ".join(current_admins)}. ' +
                               '(Restart may be required.)')
            else:
                await ctx.send('There are no current admins. (Restart may be required.)')

    @commands.command(help='Give player(s) admin permissions', name='admins-add')
    async def admins_add(self, ctx, *players):
        game = await game_mapping_helper.game_from_context(ctx, self.bot)
        if game is not None:
            await config_service.add_admins(game, players)
            await ctx.send('Admins have been added, but **you will need to restart the ' +
                           'server for this to take effect** (use `!restart`).')

    @commands.command(help='Revoke admin permissions for player(s)', name='admins-remove')
    async def admins_remove(self, ctx, *players):
        game = await game_mapping_helper.game_from_context(ctx, self.bot)
        if game is not None:
            await config_service.remove_admins(game, players)
            await ctx.send('Admins have been removed, but **you will need to restart the ' +
                           'server for this to take effect** (use `!restart`).')

    @commands.command(help='Get current config for the supplied key')
    async def config(self, ctx, key):
        game = await game_mapping_helper.game_from_context(ctx, self.bot)
        if game is not None:
            value = await config_service.get_config(game, key)
            await ctx.send(f'Config {key} is currently set to {value}. (Restart may be required.)')

    @commands.command(help='Set server config for the supplied key', name='config-set')
    async def config_set(self, ctx, key, value):
        game = await game_mapping_helper.game_from_context(ctx, self.bot)
        if game is not None:
            value = await config_service.set_config(game, key, value)
            await ctx.send(f'Config for {key} has been set, but **you will need to restart the ' +
                           'server for this to take effect** (use `!restart`).')

    @commands.command(help='Restart the server',
                      description='This is required for any config changes to take effect.')
    async def restart(self, ctx):
        game = await game_mapping_helper.game_from_context(ctx, self.bot)
        if game is not None:
            await status_service.check_game_is_running(game)
            await ctx.send('Restarting server...')
            await ecs_client.restart_service(game)
            await ctx.send('Server has been restarted :hatching_chick:')
