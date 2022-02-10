import json
import requests

import magento.config as config
from .search import SearchQuery, OrderSearch, InvoiceSearch
from .utils.UserAgent import UserAgent


class MagentoClient(object):

    def __init__(self, domain: str, username: str, password: str, user_agent: str = None, login: bool = True):

        self.BASE_URL = f'https://www.{domain}/rest/V1/'
        self.USER_CREDENTIALS = {
            'username': username,
            'password': password
        }
        self.ACCESS_TOKEN = None
        self.domain = domain
        self.user_agent = user_agent

        if not self.user_agent:
            self.user_agent = UserAgent.common().random()

        if login:
            self.authenticate()
            
    @classmethod
    def new(cls):
        return cls(
            input('Domain: '),
            input('Username: '),
            input('Password: '),
            user_agent=input('User Agent: ')
        )

    def authenticate(self) -> bool:
        """

        Send request to authentication endpoint to retrieve access token
        :return response status code of an authorized request sent to a general endpoint

        """
        url = self.BASE_URL + 'integration/admin/token'
        payload = self.USER_CREDENTIALS
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': self.user_agent
        }
        print(f'Authenticating {payload["username"]} on {self.domain}...')
        response = requests.post(url, json=payload, headers=headers)
        if response.ok:
            self.ACCESS_TOKEN = response.json()
            self.activate()

        assert self.is_active, \
            'Authentication Error\n' + \
            f'{response.status_code}' + '\n' + \
            f'{response.json()}'

        return self.validate()

    def activate(self) -> None:
        """

        Sets the active client to itself.
        If a different client is active, it is logged out.
        Called during authentication and all search queries

        """

        if isinstance(config.client, MagentoClient) and config.client is not self:
            config.client.logout()

        config.client = self

    def logout(self):
        """

        Wipes access token to ensure new one is generated next request.
        Active client is not affected unless this is the active client.

        """
        self.ACCESS_TOKEN = None

        if config.client is self:
            config.client = None

    def get(self, url: str) -> requests.Response:
        """

        Sends request with authorization token. Used for all internal requests.
        :return: response, for function specific error checking

        """
        response = requests.get(url, headers=self.headers)
        if response.status_code == 401:
            self.authenticate()
            return self.get(url)

        return response

    def validate(self):
        return self.get(self.BASE_URL + 'store/websites').status_code == 200

    def search(self, endpoint: str) -> SearchQuery:
        """

        Initiates query to a search endpoint.
        Returns a SearchQuery object.
        For some endpoints the returned object is a SearchQuery subclass with additional methods.

        :param endpoint:    the API endpoint to query

        :return:            self or subclass

        """
        self.activate()
        if endpoint.lower() == 'orders':
            return OrderSearch()
        if endpoint.lower() == 'invoices':
            return InvoiceSearch()
        if endpoint.lower() == 'string':
            pass
        else:
            return SearchQuery(endpoint)

    @staticmethod
    def save_data(data, filepath):
        with open(filepath, 'w') as data_out:
            json.dump(data, data_out, indent=4)

    @staticmethod
    def load_data(filepath):
        with open(filepath, 'r') as data_in:
            return json.load(filepath)

    def save(self):
        if self.authenticate():
            data = self.USER_CREDENTIALS.copy()
            data.update(
                {
                    'domain': self.domain,
                    'user-agent': self.user_agent
                }
            )
            self.save_data(data, self.domain)


    @property
    def token(self) -> str:
        if not self.is_active:
            self.authenticate()
        return self.ACCESS_TOKEN

    @property
    def headers(self) -> {}:
        return {
            'Authorization': f'Bearer {self.token}',
            'User-Agent': self.user_agent
        }

    @property
    def is_active(self) -> bool:
        return bool(self.ACCESS_TOKEN) and config.client is self

    @staticmethod
    def pretty(_json, sort_keys=True, **kwargs) -> None:
        print(json.dumps(_json, indent=4, sort_keys=sort_keys, **kwargs))
