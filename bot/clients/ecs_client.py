import aiobotocore


_session = aiobotocore.get_session()


async def set_desired_count(game, count):
    async with _session.create_client('ecs') as client:
        await client.update_service(
            cluster=f'{game}-cluster',
            service=f'{game}-ecs-service',
            desiredCount=count)
        await client.get_waiter('services_stable').wait(
            cluster=f'{game}-cluster',
            services=[f'{game}-ecs-service'])


async def restart_service(game):
    async with _session.create_client('ecs') as client:
        await client.update_service(
            cluster=f'{game}-cluster',
            service=f'{game}-ecs-service',
            forceNewDeployment=True)
        await client.get_waiter('services_stable').wait(
            cluster=f'{game}-cluster',
            services=[f'{game}-ecs-service'])
