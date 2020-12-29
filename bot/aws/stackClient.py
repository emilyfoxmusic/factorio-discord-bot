import aiobotocore
import logging
import os
from ..helpers.single import single

templateFile = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../aws/template.yaml'))
try:
  template = templateFile.read()
finally:
  templateFile.close()

class StackClient():
  def __init__(self):
    self._session = aiobotocore.get_session()
    logging.debug('AWS service created')

  async def create_stack(self, name, version):
    logging.debug('Creating stack with name %s and version %s' % (name, version))
    async with self._session.create_client('cloudformation') as client:
      await client.create_stack(
        StackName=name,
        TemplateBody=template,
        Parameters=[
            {
                'ParameterKey': 'FactorioImageTag',
                'ParameterValue': version,
            },
        ],
        Capabilities=['CAPABILITY_IAM']
      )
      await client.get_waiter('stack_create_complete').wait(StackName=name)
    logging.info('Created stack with name %s and version %s' % (name, version))

  async def update_stack(self, name, server_state_param):
    async with self._session.create_client('cloudformation') as client:
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
        ],
        Capabilities=['CAPABILITY_IAM']
      )
      await client.get_waiter('stack_update_complete').wait(StackName=name)

  async def delete_stack(self, name):
    logging.debug('Deleting stack with name %s' % name)
    async with self._session.create_client('cloudformation') as client:
      await client.delete_stack(StackName=name)
      await client.get_waiter('stack_delete_complete').wait(StackName=name)
    logging.info('Deleted stack with name %s' % name)
  
  async def list_stacks(self):
    logging.debug('Getting list of stacks')
    async with self._session.create_client('cloudformation') as client:
      stack_response = await client.list_stacks()
      return list(filter(lambda stack: stack['StackStatus'] != 'DELETE_COMPLETE', stack_response['StackSummaries']))

  async def stack_details(self, name):
    async with self._session.create_client('cloudformation') as client:
      stack_response = await client.describe_stacks(StackName=name)
      return stack_response['Stacks'][0]

  async def get_ec2_instance(self, name):
    async with self._session.create_client('ec2') as client:
      instances = await client.describe_instances()
      reservation = single(lambda reservation: reservation_stack_name(reservation) == name, instances['Reservations'])
      return reservation['Instances'][0]

def reservation_stack_name(reservation):
  tags = reservation['Instances'][0]['Tags']
  return single(lambda tag: tag['Key'] == 'aws:cloudformation:stack-name', tags)['Value']
