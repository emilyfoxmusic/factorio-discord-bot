import logging
import aiobotocore
from ..utilities import single


_session = aiobotocore.get_session()


async def get_ec2_instance(name):
    logging.info('Fetching info about EC2 instance for %s', name)
    async with _session.create_client('ec2') as client:
        instances = await client.describe_instances()
        reservation = single(lambda reservation:
                             reservation_stack_name(reservation) == name and
                             reservation['Instances'][0]['State']['Name'] == 'running',
                             instances['Reservations']
                             )
        return reservation['Instances'][0]


def reservation_stack_name(reservation):
    tags = reservation['Instances'][0]['Tags']
    return single(lambda tag: tag['Key'] == 'aws:cloudformation:stack-name', tags)['Value']
