from apiclient import APIClient, JsonResponseHandler


base_url = 'https://factorio.com/api'

class FactorioClient(APIClient):
  def get_latest_releases(self):
    url = f'{base_url}/latest-releases'
    return self.get(url)

client = FactorioClient(response_handler=JsonResponseHandler)