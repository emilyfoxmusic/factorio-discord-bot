from enum import Enum


class Status(Enum):
    CREATING = 1
    RUNNING = 2
    STOPPED = 3
    STARTING = 4
    STOPPING = 5
    DELETING = 6
    UNRECOGNISED = 7


def get_status(stack_status, server_state_param):
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


STATUSES_TO_MESSAGES = {
    Status.CREATING: 'The game is being created as we speak :baby:',
    Status.RUNNING: 'The game is running! Go make some factories :tada:',
    Status.STOPPED: 'The game is currently stopped. Use `!start` to play! :factory_worker:',
    Status.STARTING: 'The game is starting up... get hyped :partying_face:',
    Status.STOPPING: 'The game is shutting down... see you again soon! :cry:',
    Status.DELETING: 'The game is being deleted RIP :skull_crossbones:',
}


def message(status):
    message_for_status = STATUSES_TO_MESSAGES.get(status)
    if message_for_status is not None:
        return message_for_status
    return ('Something is amiss - the stack state is not in an expected state. ' +
            'Some debugging may be required... :detective:')
