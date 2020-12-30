from apiclient import APIClient

base_url = 'https://mods.factorio.com/api/mods'

class ModClient(APIClient):
  def get_mod(self, mod):
    url = f'{base_url}/{mod}'
    return self.get(url)