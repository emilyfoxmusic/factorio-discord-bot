from discord.ext import commands
from ..exceptions.invalidOperationException import InvalidOperationException

class CommandErrorHandler(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_command_error(self, ctx, error):
    if hasattr(error, 'original') and isinstance(error.original, InvalidOperationException):
      await ctx.send(error.original.message + ' :warning:')
    elif isinstance(error, commands.MissingRequiredArgument):
      await ctx.send(f"Oops, that's not how you use this command. Use `!help {ctx.command.name}` for more details.")
    elif isinstance(error, commands.CommandNotFound):
      await ctx.send("Sorry, I don't know how to do that :sweat_smile:. Use `!help` for info on what I can do!")
    elif isinstance(error, commands.CommandOnCooldown):
      await ctx.send('No spam plz! :octagonal_sign: (Cooldown active - try again in a bit.)')
    else:
      await ctx.send('ERROR :fire: :skull_crossbones: :fire:')