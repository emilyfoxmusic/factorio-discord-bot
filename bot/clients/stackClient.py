import aiobotocore
import logging
import os
from ..helpers.env import getenv


BOT_IP = getenv('BOT_IP')
SSH_KEY_NAME = getenv('SSH_KEY_NAME')

def get_template():
  templateFile = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../template.yaml'))
  try:
    return templateFile.read()
  finally:
    templateFile.close()

_template = get_template()
_session = aiobotocore.get_session()

async def create_stack(name, version):
  logging.info('Creating stack with name %s and version %s' % (name, version))
  async with _session.create_client('cloudformation') as client:
    await client.create_stack(
      StackName=name,
      TemplateBody=_template,
      Parameters=[
          {
              'ParameterKey': 'FactorioImageTag',
              'ParameterValue': version,
          },
          {
              'ParameterKey': 'YourIp',
              'ParameterValue': BOT_IP,
          },
          {
              'ParameterKey': 'KeyPairName',
              'ParameterValue': SSH_KEY_NAME,
          },
      ],
      Capabilities=['CAPABILITY_IAM']
    )
    await client.get_waiter('stack_create_complete').wait(
      StackName=name,
      WaiterConfig={
        'Delay': 15
      })
  logging.info('Created stack %s with version %s' % (name, version))

async def update_stack(name, server_state_param):
  logging.info('Updating stack %s to %s' % (name, server_state_param))
  async with _session.create_client('cloudformation') as client:
    await client.update_stack(
      StackName=name,
      UsePreviousTemplate=True,
      Parameters=[
        {
          'ParameterKey': 'ServerState',
          'ParameterValue': server_state_param,
        },
        {
          'ParameterKey': 'FactorioImageTag',
          'UsePreviousValue': True,
        },
        {
          'ParameterKey': 'YourIp',
          'UsePreviousValue': True,
        },
        {
          'ParameterKey': 'KeyPairName',
          'UsePreviousValue': True,
        },
      ],
      Capabilities=['CAPABILITY_IAM']
    )
    await client.get_waiter('stack_update_complete').wait(
      StackName=name,
      WaiterConfig={
        'Delay': 15
      })
  logging.info('Update for stack %s complete' % name)


async def delete_stack(name):
  logging.info('Deleting stack %s' % name)
  async with _session.create_client('cloudformation') as client:
    await client.delete_stack(StackName=name)
    await client.get_waiter('stack_delete_complete').wait(StackName=name)
  logging.info('Deleted stack with name %s' % name)

async def list_stacks():
  logging.info('Fetching list of stacks')
  async with _session.create_client('cloudformation') as client:
    stack_response = await client.describe_stacks()
    return list(filter(lambda stack: stack['StackStatus'] != 'DELETE_COMPLETE', stack_response['Stacks']))

async def stack_details(name):
  logging.info('Getting stack details for %s' % name)
  async with _session.create_client('cloudformation') as client:
    stack_response = await client.describe_stacks(StackName=name)
    return stack_response['Stacks'][0]
