from discord.ext import commands
from .cogs import (admin, auto_shutdown, backups, channel_management,
                   command_error_handler, game, healthcheck, roles)


bot = commands.Bot(command_prefix='!')

bot.add_cog(admin.Admin(bot))
bot.add_cog(auto_shutdown.AutoShutdown(bot))
bot.add_cog(channel_management.ChannelManagement(bot))
bot.add_cog(command_error_handler.CommandErrorHandler(bot))
bot.add_cog(game.Game(bot))
bot.add_cog(healthcheck.Healthcheck(bot))
bot.add_cog(roles.Roles(bot))
bot.add_cog(backups.Backups(bot))
