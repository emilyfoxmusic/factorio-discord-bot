import logging
import os
from bot.bot import bot

logging.basicConfig(format='%(asctime)s:%(module)s:%(levelname)s:%(message)s', filename="bot.log", level=logging.INFO)

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(DISCORD_TOKEN)
