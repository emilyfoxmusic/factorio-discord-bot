from enum import Enum
from ..clients import stack_client
from ..exceptions import InvalidOperationException
from ..utilities import single


class Status(Enum):
    CREATING = 1
    RUNNING = 2
    STOPPED = 3
    STARTING = 4
    STOPPING = 5
    DELETING = 6
    UNRECOGNISED = 7


async def list_game_statuses():
    stacks = await stack_client.list_stacks()
    return {stack['StackName']: _get_status_from_stack(stack) for stack in stacks}


async def get_status(name):
    stack = await stack_client.stack_details(name)
    return _get_status_from_stack(stack)


async def check_game_is_running(game):
    status = await get_status(game)
    if status != Status.RUNNING:
        raise InvalidOperationException(
            'The server must be running to do that.')


def _get_status_from_stack(stack):
    stack_status = stack['StackStatus']
    server_state_param = single(
        lambda parameter: parameter['ParameterKey'] == 'ServerState',
        stack['Parameters'])['ParameterValue']

    if stack_status == 'CREATE_IN_PROGRESS':
        return Status.CREATING
    if stack_status == 'DELETE_PENDING' or stack_status == 'DELETE_IN_PROGRESS':
        return Status.DELETING
    elif stack_status == 'CREATE_COMPLETE' or stack_status == 'UPDATE_COMPLETE':
        if server_state_param == 'Running':
            return Status.RUNNING
        elif server_state_param == 'Stopped':
            return Status.STOPPED
        else:
            raise Exception(
                f'Server state parameter: {server_state_param} is not recognised.')
    elif stack_status == 'UPDATE_IN_PROGRESS':
        if server_state_param == 'Running':
            return Status.STARTING
        elif server_state_param == 'Stopped':
            return Status.STOPPING
        else:
            raise Exception(
                f'Server state parameter: {server_state_param} is not recognised.')
    else:
        return Status.UNRECOGNISED
