import discord
from discord.ext import commands


FACTORIO_ROLE = 'Factorio'
FACTORIO_CATEGORY = 'Factorio servers'

class Roles(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
    for guild in self.bot.guilds:
      await create_role(guild)
      await create_category(guild, self.bot)

  @commands.command(help='Assign yourself the factorio role and get involved!', name="count-me-in")
  async def count_me_in(self, ctx):
    role = await get_factorio_role(ctx.guild)
    await ctx.author.add_roles(role)
    await ctx.send(f'Yay, welcome {ctx.author.mention}. I\'ve messaged you some more instructions :smiley:')
    await ctx.author.send("Hello! You should now be able to see any existing games under the 'factorio servers' category in discord (if any exist).\nI'm here to help you manage your games - I can create servers (with whatever mods you'd like), start/stop your games, take backups, and I'll even automatically stop servers when no one's using them! Use `!help` for details on the commands I understand. (I can do this in DM for your convenience.) Enjoy factorio-ing and let me know if there's anything I can help with! :partying_face:")

  @commands.command(help='Removes the factorio role so you won\'t see the games', name="count-me-out")
  async def count_me_out(self, ctx):
    role = await get_factorio_role(ctx.guild)
    await ctx.author.remove_roles(role)
    await ctx.send(f'Okay, come back soon! :cry:')

async def create_role(guild):
  role = await get_factorio_role(guild)
  if role == None:
    role = await guild.create_role(name=FACTORIO_ROLE, mentionable=False)

async def create_category(guild, bot):
  category = discord.utils.get(guild.categories, name=FACTORIO_CATEGORY)
  if category == None:
    factorio_role = await get_factorio_role(guild)
    bot_role = get_bot_role(guild, bot)
    overwrites = {
      guild.default_role: discord.PermissionOverwrite(view_channel=False),
      factorio_role: discord.PermissionOverwrite(view_channel=True),
      bot_role: discord.PermissionOverwrite(view_channel=True)
    }
    await guild.create_category(FACTORIO_CATEGORY, overwrites=overwrites)

async def get_factorio_role(guild):
  roles = await guild.fetch_roles()
  return discord.utils.get(roles, name=FACTORIO_ROLE)

def get_bot_role(guild, bot):
  bot_role = list(filter(lambda role: not role.is_default(), guild.get_member(bot.user.id).roles))
  if len(bot_role) > 1:
    raise Exception('Bot has multiple roles')
  if len(bot_role) == 0:
    raise Exception('Bot role not found')
  return bot_role[0]