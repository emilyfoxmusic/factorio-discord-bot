import paramiko
import os

SSH_KEY_LOCATION = os.getenv('SSH_KEY_LOCATION')

class SshService():  
  def exec(self, ip, commands):
    client = paramiko.SSHClient()
    try:
      client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      client.connect(ip, username='ec2-user', key_filename=SSH_KEY_LOCATION)
      for command in commands:
        stdin, stdout, stderr = client.exec_command(command)
        for line in stdout:
          print(line)
        for line in stderr:
          print(line)
    finally:
      client.close()
