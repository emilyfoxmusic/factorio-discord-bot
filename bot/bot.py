from discord.ext import commands
from .cogs import admin, autoShutdown, backups, channelManagement, commandErrorHandler, game, healthcheck, roles


bot = commands.Bot(command_prefix='!')

bot.add_cog(admin.Admin(bot))
bot.add_cog(autoShutdown.AutoShutdown(bot))
bot.add_cog(channelManagement.ChannelManagement(bot))
bot.add_cog(commandErrorHandler.CommandErrorHandler(bot))
bot.add_cog(game.Game(bot))
bot.add_cog(healthcheck.Healthcheck(bot))
bot.add_cog(roles.Roles(bot))
bot.add_cog(backups.Backups(bot))