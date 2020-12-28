import aiobotocore
import logging

from aws.template import template


class AwsService():
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

  async def delete_stack(self, name):
    logging.debug('Deleting stack with name %s' % name)
    
    async with self._session.create_client('cloudformation') as client:
      await client.delete_stack(StackName=name)
      await client.get_waiter('stack_delete_complete').wait(StackName=name)

    logging.info('Deleted stack with name %s' % (name))
  
  async def list_stacks(self):
    logging.debug('Getting list of stacks')

    async with self._session.create_client('cloudformation') as client:
      stack_response = await client.list_stacks()
      return list(filter(lambda stack: stack['StackStatus'] != 'DELETE_COMPLETE', stack_response['StackSummaries']))
