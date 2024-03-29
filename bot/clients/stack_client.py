import logging
import os
import aiobotocore
from ..helpers.env import getenv


BOT_IP = getenv('BOT_IP')
SSH_KEY_NAME = getenv('SSH_KEY_NAME')


def get_template():
    with open(
            os.path.join(os.path.dirname(
                os.path.abspath(__file__)), '../template.yaml'),
            encoding="utf8") as template_file:
        return template_file.read()


_template = get_template()
_session = aiobotocore.get_session()


async def create_stack(name, version):
    logging.info('Creating stack with name %s and version %s',
                 name, version)

    async with _session.create_client('ec2') as ec2_client:
        logging.info('Fetching VPC information')
        # Assume that the account has a single default VPC
        vpc_id = (await ec2_client.describe_vpcs(Filters=[{
            'Name': 'is-default',
            'Values': ['true']
        }]))['Vpcs'][0]['VpcId']
        subnets = await ec2_client.describe_subnets(Filters=[{
            'Name': 'vpc-id',
            'Values': [vpc_id]}])
        subnet_a = subnets['Subnets'][0]['SubnetId']
        subnet_b = subnets['Subnets'][1]['SubnetId']
        async with _session.create_client('cloudformation') as cloudformation_client:
            logging.info('Creating stack')
            await cloudformation_client.create_stack(
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
                    {
                        'ParameterKey': 'VpcId',
                        'ParameterValue': vpc_id,
                    },
                    {
                        'ParameterKey': 'SubnetA',
                        'ParameterValue': subnet_a,
                    },
                    {
                        'ParameterKey': 'SubnetB',
                        'ParameterValue': subnet_b,
                    }
                ],
                Capabilities=['CAPABILITY_IAM']
            )
            await cloudformation_client.get_waiter('stack_create_complete').wait(
                StackName=name,
                WaiterConfig={
                    'Delay': 15
                })
        logging.info('Created stack %s with version %s', name, version)


async def update_stack(name, server_state_param):
    logging.info('Updating stack %s to %s', name, server_state_param)
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
                {
                    'ParameterKey': 'VpcId',
                    'UsePreviousValue': True,
                },
                {
                    'ParameterKey': 'SubnetA',
                    'UsePreviousValue': True,
                },
                {
                    'ParameterKey': 'SubnetB',
                    'UsePreviousValue': True,
                }
            ],
            Capabilities=['CAPABILITY_IAM']
        )
        await client.get_waiter('stack_update_complete').wait(
            StackName=name,
            WaiterConfig={
                'Delay': 15
            })
    logging.info('Update for stack %s complete', name)


async def delete_stack(name):
    logging.info('Deleting stack %s', name)
    async with _session.create_client('cloudformation') as client:
        await client.delete_stack(StackName=name)
        await client.get_waiter('stack_delete_complete').wait(StackName=name)
    logging.info('Deleted stack with name %s', name)


async def list_stacks():
    logging.info('Fetching list of stacks')
    async with _session.create_client('cloudformation') as client:
        stack_response = await client.describe_stacks()
        return list(
            filter(
                lambda stack: stack['StackStatus'] != 'DELETE_COMPLETE',
                stack_response['Stacks']))


async def stack_details(name):
    logging.info('Getting stack details for %s', name)
    async with _session.create_client('cloudformation') as client:
        stack_response = await client.describe_stacks(StackName=name)
        return stack_response['Stacks'][0]
