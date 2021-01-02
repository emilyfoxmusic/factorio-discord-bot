import paramiko
import os


SSH_KEY_LOCATION = os.getenv('SSH_KEY_LOCATION')

def exec(hostname, *commands):
  client = paramiko.SSHClient()
  try:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username='ec2-user', key_filename=SSH_KEY_LOCATION)
    for command in commands:
      stdin, stdout, stderr = client.exec_command(command)
      for line in stdout:
        print(line)
      for line in stderr:
        print(line)
  finally:
    client.close()

def exec_get(hostname, command):
  client = paramiko.SSHClient()
  try:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username='ec2-user', key_filename=SSH_KEY_LOCATION)
    stdin, stdout, stderr = client.exec_command(command)
    # TODO: throw here if stderr is not empty
    return stdout.read().decode("utf-8").strip('\n')
  finally:
    client.close()