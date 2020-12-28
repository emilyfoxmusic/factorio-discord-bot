from discord.ext import commands

from .controllers.admin import Admin
from .controllers.healthcheck import Healthcheck
from .controllers.game import Game

bot = commands.Bot(command_prefix='!')
bot.add_cog(Healthcheck(bot))
bot.add_cog(Admin(bot))
bot.add_cog(Game(bot))