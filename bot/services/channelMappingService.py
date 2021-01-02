import discord
from ..clients import channelMappingClient
from ..services import gameService

async def init_channel_table():
  if not await channelMappingClient.check_table_exists():
    await channelMappingClient.create_table()

async def get_game_channel_mappings(name):
  await channelMappingClient.get_mappings(name)

async def set_channel_mapping(name, guild_id, channel_id):
  await channelMappingClient.set_mapping(name, guild_id, channel_id)

async def get_game(guild_id, channel_id):
  return await channelMappingClient.get_associated_game(guild_id, channel_id)

async def remove_mappings(guild_id, channel_id=None):
  if channel_id == None:
    await channelMappingClient.delete_guild_mappings(guild_id)
  else:
    await channelMappingClient.delete_mappings([{ 'guild_id': guild_id, 'channel_id': channel_id }])

async def validate_mappings(bot):
  all_mappings = await channelMappingClient.get_all_mappings()
  games = await gameService.list_games()
  invalid_mappings = list(filter(lambda mapping: not mapping_is_valid(mapping, bot, games), all_mappings))
  if len(invalid_mappings) > 0:
    await channelMappingClient.delete_mappings(invalid_mappings)

def mapping_is_valid(mapping, bot, games):
  if mapping['game'] not in games:
    return False
  guild = discord.utils.get(bot.guilds, id=mapping['guild_id'])
  if guild == None:
    return False
  channel = discord.utils.get(guild.channels, id=mapping['channel_id'])
  return channel != None