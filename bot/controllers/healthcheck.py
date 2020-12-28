from discord.ext import commands

class Healthcheck(commands.Cog):
  def __init__(self, bot):
      self.bot = bot

  @commands.command(help='Test')
  async def test(self, ctx):
    await ctx.send('Hi')
