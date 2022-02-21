import copy
import json
import requests
import magento.config as config
from .search import SearchQuery, OrderSearch, InvoiceSearch, CategorySearch
from .utils.UserAgent import UserAgent


class Client(object):

    def __init__(self, domain, username, password, user_agent=None, token=None, login=True):
        self.BASE_URL = f'https://www.{domain}/rest/V1/'
        self.USER_CREDENTIALS = {
            'username': username,
            'password': password
        }
        self.ACCESS_TOKEN = token
        self.domain = domain
        self.user_agent = user_agent if user_agent else UserAgent().default
        self.activate()

        if login:
            self.validate()

    @classmethod
    def from_json(cls, json_str):
        kwargs = json.loads(json_str)
        return cls(**kwargs)

    # return json.loads(data.decode('utf-8'))
    @classmethod
    def new(cls):
        return cls(
            input('Domain: '),
            input('Username: '),
            input('Password: '),
            user_agent=input('User Agent: ')
        )

    @property
    def orders(self):
        return OrderSearch()

    @property
    def invoices(self):
        return InvoiceSearch()

    @property
    def categories(self):
        return CategorySearch()

    def authenticate(self) -> None:
        """
        Requests a token from the authentication endpoint. If successful, sets active client to itself.
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

        if self.validate():
            print('Login successful')
        else:
            raise AuthenticationError(f'{response.json()}')

    def search(self, endpoint: str) -> SearchQuery:
        """
        Initiates query to a search endpoint and returns a SearchQuery object.
        Some endpoints return SearchQuery subclass objects that have additional methods.

        """
        self.activate()
        if endpoint.lower() == 'orders':
            return OrderSearch()
        if endpoint.lower() == 'invoices':
            return InvoiceSearch()
        if endpoint.lower() == 'categories':
            return CategorySearch()
        if endpoint.lower() == 'string':
            pass
        else:
            return SearchQuery(endpoint)

    def activate(self) -> None:
        """
        Sets the active client to itself. If a different client was active, it is logged out.
        Called during authentication and all search queries.

        """
        if isinstance(config.client, Client) and config.client is not self:
            config.client.logout()
        config.client = self

    def validate(self):
        """Checks active client and sends an authorized request to a standard API endpoint"""
        return config.client is self and self.request(self.BASE_URL + 'store/websites').status_code == 200

    def logout(self):
        """Deletes the access token and, if currently active, resets the active client"""
        if config.client is self:
            config.client = None
        self.ACCESS_TOKEN = None

    def request(self, url) -> requests.Response:
        """Sends a request with the access token. Used for all internal requests"""
        response = requests.get(url, headers=self.headers)
        if response.status_code == 401:
            self.authenticate()
            return self.request(url)
        return response

    def to_json(self, validate=False):
        """Validates and saves login credentials for this domain"""
        data = copy.deepcopy(self.USER_CREDENTIALS)
        if validate:
            try:
                self.validate()
            except AuthenticationError as e:
                return e.args
        data.update(
            {  # Add more to this if you want!
                'domain': self.domain,
                'user_agent': self.user_agent,
                'token': self.token
            }
        )
        return json.dumps(data)

    @property
    def headers(self) -> {}:
        """Any time this is called, the token is validated"""
        return {
            'Authorization': f'Bearer {self.token}',
            'User-Agent': self.user_agent
        }

    @property
    def token(self) -> str:
        """Returns a valid access token"""
        if not self.ACCESS_TOKEN:
            self.authenticate()
        return self.ACCESS_TOKEN

    @staticmethod
    def save_data(data, filepath):
        with open(filepath, 'w') as data_out:
            json.dump(data, data_out, indent=4)

    @staticmethod
    def load_data(filepath):
        with open(filepath, 'r') as data_in:
            return json.load(filepath)

    @staticmethod
    def pretty(_json, sort_keys=True, **kwargs) -> None:
        print(json.dumps(_json, indent=4, sort_keys=sort_keys, **kwargs))


class AuthenticationError(Exception):
    pass
