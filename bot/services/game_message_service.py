import discord
from ..utilities import single
from ..clients import channel_mapping_client


async def send_shutdown_notification(bot, game):
    for channel in await get_game_channels(bot, game):
        await channel.send('Server is shutting down due to inactivity :sob:')


async def send_shutdown_finished(bot, game):
    for channel in await get_game_channels(bot, game):
        await channel.send('Server has shut down, come back soon! :wave:')


async def send_shutdown_failed(bot, game):
    for channel in await get_game_channels(bot, game):
        await channel.send('@here I tried to shut down this server but I failed :cry:. ' +
                           'I will forcefully shut it down soon (without guaranteeing a backup). ' +
                           'Use `!let-me-live` to keep it alive for longer.')


async def send_unknown_idle_status_message(bot, game):
    for channel in await get_game_channels(bot, game):
        await channel.send('@here I failed to connect to this game to work out if there is ' +
                           'anyone playing. I will shut it down soon if I continue to be ' +
                           'unable to connect. Use `!let-me-live` to keep it alive for longer.')


async def send_shutdown_warning(bot, game):
    for channel in await get_game_channels(bot, game):
        await channel.send('Server will shut down soon due to inactivity ' +
                           '- use `!let-me-live` to keep it alive for longer.')


async def send_idle_message(bot, game):
    for channel in await get_game_channels(bot, game):
        await channel.send("It's looking very quiet in here :eyes:")


def channel_selector(mapping):
    return lambda channel: channel.id == mapping['channel_id']


async def get_game_channels(bot, game):
    mappings = await channel_mapping_client.get_mappings(game)
    channels = []
    for mapping in mappings:
        guild = discord.utils.get(bot.guilds, id=mapping['guild_id'])
        game_channel = single(channel_selector(mapping), guild.channels)
        channels.append(game_channel)
    return channels
