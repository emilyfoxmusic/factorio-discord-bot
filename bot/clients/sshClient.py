import paramiko
import logging
from ..helpers.env import getenv


SSH_KEY_LOCATION = getenv('SSH_KEY_LOCATION')

def exec(hostname, *commands):
  client = paramiko.SSHClient()
  try:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username='ec2-user', key_filename=SSH_KEY_LOCATION)
    for command in commands:
      stdin, stdout, stderr = client.exec_command(command)
      for line in stdout:
        logging.info(line)
      for line in stderr:
        logging.info(line)
  finally:
    client.close()

def exec_get(hostname, command):
  client = paramiko.SSHClient()
  try:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username='ec2-user', key_filename=SSH_KEY_LOCATION)
    stdin, stdout, stderr = client.exec_command(command)
    return stdout.read().decode("utf-8").strip('\n')
  finally:
    client.close()