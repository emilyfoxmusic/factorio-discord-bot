import logging
import os

import discord
from discord.ext import commands


bot = commands.Bot(command_prefix='!')

@bot.command(help='Test')
async def test(ctx):
    await ctx.send('Hi!')

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(DISCORD_TOKEN)
