import logging
import os

import discord
from discord.ext import commands

from services.aws import AwsService

bot = commands.Bot(command_prefix='!')
aws = AwsService()

@bot.command(help='Create a new game')
async def new(ctx):
  logging.info('Received command: `!new`')
  # Check params then
  try:
    await ctx.send('Creating new game :star2:')
    await aws.create_stack('factorio-test3', 'latest')
    await ctx.send('Done!')
  except:
    await ctx.send('ERROR :fire:')

@bot.command(help='Test')
async def test(ctx):
  await ctx.send('Hi!')

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(DISCORD_TOKEN)
