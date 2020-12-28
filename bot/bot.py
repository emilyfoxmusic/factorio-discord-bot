import logging
import os

import discord
from discord.ext import commands

from services.aws import AwsService

bot = commands.Bot(command_prefix='!')
aws = AwsService()

@bot.command(help='Create a new game')
async def new(ctx, *args):
  logging.info('Received command: `!new`')
  if len(args) == 0:
    await ctx.send('Please provide a name for the game.')
    return

  name = args[0]
  version = args[1] if len(args) > 1 else 'latest'
  try:
    await ctx.send('Creating new game :star2:')
    await aws.create_stack(name, version)
    await ctx.send('Done!')
  except:
    await ctx.send('ERROR :fire:')

@bot.command(help='Delete a game')
async def delete(ctx, *args):
  if len(args) == 0:
    await ctx.send('Please specify the game to delete.')
    return

  name = args[0]
  try:
    await ctx.send('Deleting the game')
    await aws.delete_stack(name)
    await ctx.send("Done!")
  except:
    await ctx.send('ERROR :fire:')

@bot.command(help='Lists all games')
async def list(ctx):
  await ctx.send('Getting list of games')
  stacks = await aws.list_stacks()
  if (len(stacks) == 0):
    await ctx.send('There are no games active at the moment. Create a new one with `!new`.')
    return
  for stack in stacks:
    await ctx.send(stack['StackName'] + ': ' + stack['StackStatus'])

@bot.command(help='Test')
async def test(ctx, *args):
  await ctx.send('Hi!')


DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(DISCORD_TOKEN)
