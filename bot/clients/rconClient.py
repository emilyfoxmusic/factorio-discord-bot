import factorio_rcon


class RconClient():
  def __init__(self, ip, rcon_pw):
    self.ip = ip
    self.rcon_pw = rcon_pw

  def game_time(self):
    rcon_client = factorio_rcon.RCONClient(self.ip, 27015, self.rcon_pw)
    try:
      return rcon_client.send_command("/time")
    finally:
      rcon_client.close()

  def save(self):
    rcon_client = factorio_rcon.RCONClient(self.ip, 27015, self.rcon_pw)
    try:
      return rcon_client.send_command("/server-save")
    finally:
      rcon_client.close()