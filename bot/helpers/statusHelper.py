def interpret_status(stack_status, server_state_param):
  if stack_status == 'CREATE_IN_PROGRESS':
    return 'The game is being created as we speak :arrows_counterclockwise:'
  elif stack_status == 'CREATE_COMPLETE' or stack_status == 'UPDATE_COMPLETE':
    if server_state_param == 'Running':
      return 'The game is running! Go make some factories :tada:'
    elif server_state_param == 'Stopped':
      return 'The game is currently stopped. Use `!start` to play! :factory_worker:'
    else:
      raise Exception(f'Server state parameter: {server_state_param} is not recognised.')
  else:
    return f'Something is amiss - the stack state is {stack_status}, which is unexpected. Some debugging may be required... :detective:'