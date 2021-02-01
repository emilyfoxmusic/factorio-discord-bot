import logging
from bot.bot import bot
from .helpers.env import getenv


logging.basicConfig(format='%(asctime)s:%(module)s:%(levelname)s:%(message)s', filename="bot.log", level=logging.INFO)

DISCORD_TOKEN = getenv('DISCORD_TOKEN')
bot.run(DISCORD_TOKEN)
