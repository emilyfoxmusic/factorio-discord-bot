from apiclient import APIClient, JsonResponseHandler


BASE_URL = 'https://mods.factorio.com/api/mods'


class ModClient(APIClient):
    def get_mod(self, mod):
        url = f'{BASE_URL}/{mod}'
        return self.get(url)


client = ModClient(response_handler=JsonResponseHandler)
