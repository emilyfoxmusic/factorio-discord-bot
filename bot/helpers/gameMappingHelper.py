from discord import ChannelType
from ..services import channelMappingService, gameService


async def game_from_context(ctx, bot):
  if ctx.channel.type == ChannelType.private:
    await ctx.send("Sorry, I can't do that in DM.")
    return
  game = await channelMappingService.get_game(ctx.channel.guild.id, ctx.channel.id)
  if game == None:
    await ctx.send('This channel does not have an associated game - use `!set-channel` to assign a game to this channel.')
  elif not await gameService.game_exists(game):
    # We've hit a state we shouldn't be in! Clear up the mappings:
    await channelMappingService.validate_mappings(bot)
    await ctx.send('The game associated with this channel no longer exists - use `!set-channel` to assign a new game to this channel.')
  return game