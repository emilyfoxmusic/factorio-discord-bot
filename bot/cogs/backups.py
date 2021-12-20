import discord
from discord.ext import commands
from ..services import backup_service, status_service
from ..helpers import game_mapping_helper
from ..services.status_service import Status


class Backups(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await backup_service.init_backup_bucket()

    @commands.command(help='Take a backup and post a download link',
                      description='The game must be running for this command to work. ' +
                      'Note backups are always taken automatically on stopping or ' +
                      'deleting a server.')
    async def backup(self, ctx):
        game = await game_mapping_helper.game_from_context(ctx, self.bot)
        if game is not None:
            status = await status_service.get_status(game)
            if status == Status.RUNNING:
                await ctx.send('Taking a backup now...')
                await backup_service.backup(game)
                await self.list_backups(ctx, 1)
            else:
                await ctx.send(
                    'Backups can only be taken when the server is running :no_entry_sign:\n' +
                    'Note: backups are taken automatically when a server is stopped. You can ' +
                    'use `!list-backups` to see the latest backup.')

    @commands.command(name='list-backups',
                      help='Get the latest backup(s) for the game',
                      usage='[number=1] [game=associated with channel]')
    async def list_backups(self, ctx, *args):
        number = int(args[0]) if len(args) > 0 else 1
        game = (args[1] if len(args) > 1
                else await game_mapping_helper.game_from_context(ctx, self.bot))
        if game is not None:
            backups = await backup_service.list_backups(game)
            backups.sort(key=lambda backup: backup['taken_at'], reverse=True)
            backups = backups[:number]
            if len(backups) == 0:
                await ctx.send(f"No backups found for '{game}' :skull:")
            for backup in backups:
                taken_at = backup['taken_at']
                embedded_link = discord.Embed(
                    title=f'{game}-' + backup['title'],
                    url=backup['url'],
                    description=f'Backup taken: {taken_at:%d, %b %Y %H:%M}.')
                await ctx.send(embed=embedded_link)
