import aiobotocore
import logging
import os


REGION = os.getenv('AWS_DEFAULT_REGION')

_session = aiobotocore.get_session()

async def get_buckets():
  async with _session.create_client('s3') as client:
    response = await client.list_buckets()
    return response['Buckets']

async def create_bucket(bucket_name):
  logging.info('Creating bucket for %s' % bucket_name)
  async with _session.create_client('s3') as client:
    await client.create_bucket(
      ACL='public-read',
      Bucket=bucket_name,
      CreateBucketConfiguration={
        'LocationConstraint': REGION
      }
    )

async def list_objects(bucket_name):
  async with _session.create_client('s3') as client:
    object_response = await client.list_objects(Bucket=bucket_name)
    return object_response['Contents']