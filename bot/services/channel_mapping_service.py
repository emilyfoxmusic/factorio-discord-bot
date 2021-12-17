import discord
from ..clients import channel_mapping_client
from ..services import game_service


async def init_channel_table():
    if not await channel_mapping_client.check_table_exists():
        await channel_mapping_client.create_table()


async def get_game_channel_mappings(name):
    await channel_mapping_client.get_mappings(name)


async def set_channel_mapping(name, guild_id, channel_id):
    await channel_mapping_client.set_mapping(name, guild_id, channel_id)


async def get_game(guild_id, channel_id):
    return await channel_mapping_client.get_associated_game(guild_id, channel_id)


async def remove_mappings(guild_id, channel_id=None):
    if channel_id is None:
        await channel_mapping_client.delete_guild_mappings(guild_id)
    else:
        await channel_mapping_client.delete_mappings([{
            'guild_id': guild_id,
            'channel_id': channel_id
        }])


async def validate_mappings(bot):
    all_mappings = await channel_mapping_client.get_all_mappings()
    games = await game_service.list_games()
    invalid_mappings = list(
        filter(lambda mapping: not mapping_is_valid(mapping, bot, games), all_mappings))
    if len(invalid_mappings) > 0:
        await channel_mapping_client.delete_mappings(invalid_mappings)


def mapping_is_valid(mapping, bot, games):
    if mapping['game'] not in games:
        return False
    guild = discord.utils.get(bot.guilds, id=mapping['guild_id'])
    if guild is None:
        return False
    channel = discord.utils.get(guild.channels, id=mapping['channel_id'])
    return channel is not None
