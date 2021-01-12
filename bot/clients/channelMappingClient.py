import aiobotocore


CHANNEL_TABLE = 'FactorioChannelMapping'

_session = aiobotocore.get_session()

async def check_table_exists():
  async with _session.create_client('dynamodb') as client:
    tables = await client.list_tables()
    return CHANNEL_TABLE in tables['TableNames']

async def create_table():
  async with _session.create_client('dynamodb') as client:
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
    await client.get_waiter('table_exists').wait(
      TableName=CHANNEL_TABLE,
      WaiterConfig={
        'Delay': 10
      })

async def get_associated_game(guild_id, channel_id):
  async with _session.create_client('dynamodb') as client:
    mapping_for_channel = await client.get_item(
      TableName=CHANNEL_TABLE,
      Key={
        'GuildId': { 'S' : str(guild_id) },
        'ChannelId': { 'S': str(channel_id) }
      }
    )
    if 'Item' in mapping_for_channel:
      return mapping_for_channel['Item']['GameName']['S']
    return None

async def get_mappings(name):
  async with _session.create_client('dynamodb') as client:
    mappings_response = await client.scan(
      TableName=CHANNEL_TABLE,
      FilterExpression="GameName = :gamename",
      ExpressionAttributeValues={ ":gamename": { "S": name } }
    )
  return map(map_item, mappings_response['Items'])

async def set_mapping(name, guild_id, channel_id):
    async with _session.create_client('dynamodb') as client:
      await client.put_item(
        TableName=CHANNEL_TABLE,
        Item={
          'GuildId': { 'S' : str(guild_id) },
          'ChannelId': { 'S': str(channel_id) },
          'GameName': { 'S': name }
        })

async def delete_guild_mappings(guild_id):
  async with _session.create_client('dynamodb') as client:
    mappings_response = await client.scan(
      TableName=CHANNEL_TABLE,
      KeyConditionExpression="GuildId = :guildid",
      ExpressionAttributeValues={ ":guildid": { "S": str(guild_id) } }
    )
  if 'Items' in mappings_response and len(mappings_response['Items']) > 0:
    await delete_mappings(map(map_item, mappings_response['Items']))

async def delete_mappings(mappings):
  async with _session.create_client('dynamodb') as client:
      await client.batch_write_item(
        RequestItems={
          CHANNEL_TABLE: list(map(lambda mapping: {
            'DeleteRequest': {
              'Key': {
                'GuildId': { 'S' : str(mapping['guild_id']) },
                'ChannelId': { 'S': str(mapping['channel_id']) }
              }
            }
          }, mappings))
        }
      )

async def get_all_mappings():
  async with _session.create_client('dynamodb') as client:
    mappings_response = await client.scan(TableName=CHANNEL_TABLE)
    return map(map_item, mappings_response.get('Items'))

def map_item(item):
  return { 'guild_id': int(item['GuildId']['S']), 'channel_id': int(item['ChannelId']['S']), 'game': item['GameName']['S'] }