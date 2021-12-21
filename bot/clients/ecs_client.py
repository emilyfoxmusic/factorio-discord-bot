import aiobotocore


_session = aiobotocore.get_session()


def _cluster_name(game):
    return f'{game}-cluster'


def _service_name(game):
    return f'{game}-ecs-service'


async def set_desired_count(game, count):
    async with _session.create_client('ecs') as client:
        await client.update_service(
            cluster=_cluster_name(game),
            service=_service_name(game),
            desiredCount=count)
        await client.get_waiter('services_stable').wait(
            cluster=_cluster_name(game),
            services=[_service_name(game)])


async def restart_service(game):
    async with _session.create_client('ecs') as client:
        await client.update_service(
            cluster=_cluster_name(game),
            service=_service_name(game),
            forceNewDeployment=True)
        await client.get_waiter('services_stable').wait(
            cluster=_cluster_name(game),
            services=[_service_name(game)])


async def get_stable_running_task_count(game):
    async with _session.create_client('ecs') as client:
        await client.get_waiter('services_stable').wait(
            cluster=_cluster_name(game),
            services=[_service_name(game)],
            WaiterConfig={
                'Delay': 30,
                'MaxAttempts': 4
            }
        )
        services = await client.describe_services(
            cluster=_cluster_name(game),
            services=[_service_name(game)])
        return services['services'][0]['runningCount']
