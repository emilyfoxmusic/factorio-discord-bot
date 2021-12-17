from apiclient import APIClient, JsonResponseHandler


BASE_URL = 'https://factorio.com/api'


class FactorioClient(APIClient):
    def get_latest_releases(self):
        url = f'{BASE_URL}/latest-releases'
        return self.get(url)


client = FactorioClient(response_handler=JsonResponseHandler)
