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

