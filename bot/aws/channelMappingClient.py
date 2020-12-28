import aiobotocore
import logging

CHANNEL_TABLE = 'FactorioChannelMapping'

class ChannelMappingClient():
  def __init__(self):
    self._session = aiobotocore.get_session()

  async def check_table_exists(self):
    async with self._session.create_client('dynamodb') as client:
      tables = await client.list_tables()
      return CHANNEL_TABLE in tables['TableNames']

  async def create_table(self):
    async with self._session.create_client('dynamodb') as client:
      await client.create_table(
        AttributeDefinitions=[
          {
            'AttributeName': 'GuildId',
            'AttributeType': 'S'
          },
          {
            'AttributeName': 'ChannelId',
            'AttributeType': 'S'
          },
        ],
        TableName=CHANNEL_TABLE,
        KeySchema=[
          {
            'AttributeName': 'GuildId',
            'KeyType': 'HASH'
          },
          {
            'AttributeName': 'ChannelId',
            'KeyType': 'RANGE'
          },
        ],
        BillingMode='PAY_PER_REQUEST')

  async def get_mappings(self, name):
    async with self._session.create_client('dynamodb') as client:
      existing_mappings = await client.scan(
        TableName=CHANNEL_TABLE,
        FilterExpression="GameName = :gamename",
        ExpressionAttributeValues={ ":gamename": { "S": name } }
      )
      print(existing_mappings)
  
  async def set_mapping(self, name, guild_id, channel_id):
    async with self._session.create_client('dynamodb') as client:
      await client.put_item(
        TableName=CHANNEL_TABLE,
        Item={
          'GuildId': { 'S' : str(guild_id) },
          'ChannelId': { 'S': str(channel_id) },
          'GameName': { 'S': name }
        })
