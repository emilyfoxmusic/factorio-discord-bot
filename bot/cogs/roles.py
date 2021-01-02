import discord
from discord.ext import commands


ADMIN_ROLE = 'Factorio-Admin'

class Roles(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
    for guild in self.bot.guilds:
      roles = await guild.fetch_roles()
      admin_role = discord.utils.get(roles, name=ADMIN_ROLE)
      if admin_role == None:
        await guild.create_role(name=ADMIN_ROLE, mentionable=True)
