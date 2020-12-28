from discord.ext import commands

from .cogs.admin import Admin
from .cogs.healthcheck import Healthcheck
from .cogs.game import Game
from .cogs.errorHandling import CommandErrorHandler

bot = commands.Bot(command_prefix='!')
bot.add_cog(Healthcheck(bot))
bot.add_cog(Admin(bot))
bot.add_cog(Game(bot))
bot.add_cog(CommandErrorHandler(bot))