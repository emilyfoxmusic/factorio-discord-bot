import factorio_rcon


class RconClient():
    def __init__(self, ip, rcon_pw):
        self.ip = ip
        self.rcon_pw = rcon_pw

    def _send_command(self, command):
        rcon_client = factorio_rcon.RCONClient(self.ip, 27015, self.rcon_pw)
        try:
            return rcon_client.send_command(command)
        finally:
            rcon_client.close()

    def game_time(self):
        return self._send_command("/time")

    def save(self):
        return self._send_command("/server-save")
