import json
import requests
import settings.config as config
from search import *


class MagentoClient(object):

    def __init__(self, domain: str, username: str, password: str):

        self.BASE_URL = f'https://www.{domain}/rest/V1/'
        self.USER_CREDENTIALS = {
            'username': username,
            'password': password
        }
        self.ACCESS_TOKEN = None
        config.client = self

    def authenticate(self) -> None:
        url = self.BASE_URL + 'integration/admin/token'
        payload = self.USER_CREDENTIALS
        headers = {'Content-Type': 'application/json'}

        response = requests.post(url, json=payload, headers=headers)
        if response.ok:
            self.ACCESS_TOKEN = response.json()
        if not self.is_active:
            raise ResourceWarning(f'Login Failed\n{response.status_code}\n{response.json()}')

    def get(self, url: str) -> requests.Response:
        # Will always verify token via self.headers -> self.token -> self.is_active -> self.authenticate()
        return requests.get(url, headers=self.headers)

    def search(self, endpoint: str) -> SearchQuery:
        if endpoint in ['orders', 'Orders']:
            return OrderSearch()
        if endpoint in ['invoices', 'Invoices']:
            return InvoiceSearch()
        if endpoint == 'string':
            pass
        else:
            return SearchQuery(endpoint)

    @property
    def token(self) -> str:
        if not self.is_active:
            self.authenticate()
        return self.ACCESS_TOKEN

    @property
    def headers(self) -> {}:
        return {'Authorization': f'Bearer {self.token}'}

    @property
    def is_active(self) -> bool:
        return bool(self.ACCESS_TOKEN)

    @staticmethod
    def pretty(_json, sort_keys=True) -> None:
        print(json.dumps(_json, indent=4, sort_keys=sort_keys))
