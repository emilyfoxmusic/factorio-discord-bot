import logging
from discord.ext import commands
from ..services.aws import AwsService
from ..services.channelService import ChannelService

class Admin(commands.Cog):
  def __init__(self, bot):
      self.bot = bot
      self.aws = AwsService()
      self.channels = ChannelService()

  @commands.Cog.listener()
  async def on_ready(self):
    print('I am here!')
    await self.channels.init_channel_table()

  @commands.command(help='Create a new game', usage='<name> [version]')
  async def new(self, ctx, name, *args):
    logging.info('Received command: `!new`')
    version = args[0] if len(args) > 0 else 'latest'
    try:
      await ctx.send('Creating new game :star2:')
      await self.aws.create_stack(name, version)
      await ctx.send('Done!')
    except:
      await ctx.send('ERROR :fire:')

  @commands.command(help='Delete a game')
  async def delete(self, ctx, name):
    logging.info('Received command: `!delete`')
    try:
      await ctx.send('Deleting the game')
      await self.aws.delete_stack(name)
      await ctx.send("Done!")
    except:
      await ctx.send('ERROR :fire:')

  @commands.command(help='List all active games')
  async def list(self, ctx):
    logging.info('Received command: `!list`')
    stacks = await self.aws.list_stacks()
    if (len(stacks) == 0):
      await ctx.send('There are no games active at the moment. Create a new one with `!new`.')
      return
    for stack in stacks:
      await ctx.send(stack['StackName'] + ': ' + stack['StackStatus'])

  @commands.command(name="set-game", help='Link the current channel to the specified game')
  async def set_game(self, ctx, name):
    logging.info('Received command: `!set_game`')
    await self.channels.set_channel_mapping(name, ctx.channel.guild.id, ctx.channel.id)
