import discord
from ..utilities import single
from ..clients import channelMappingClient


async def send_shutdown_notification(bot, game):
  for channel in await get_game_channels(bot, game):
    await channel.send('Server is shutting down due to inactivity :sob:')

async def send_shutdown_finished(bot, game):
  for channel in await get_game_channels(bot, game):
    await channel.send('Server has shut down, come back soon! :wave:')

async def send_shutdown_warning(bot, game):
  for channel in await get_game_channels(bot, game):
    await channel.send('Server will shut down soon due to inactivity - use `!letmelive` to keep it alive for longer.')

async def send_idle_message(bot, game):
  for channel in await get_game_channels(bot, game):
    await channel.send("It's looking very quiet in here :eyes:")

async def get_game_channels(bot, game):
  mappings = await channelMappingClient.get_mappings(game)
  channels = []
  for mapping in mappings:
    guild = discord.utils.get(bot.guilds, id=mapping['guild_id'])
    game_channel = single(lambda channel: channel.id == mapping['channel_id'], guild.channels)
    channels.append(game_channel)
  return channels