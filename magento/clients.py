from __future__ import annotations
import json
import copy
import requests
from .utils import get_agent
from .search import SearchQuery, OrderSearch, ProductSearch, InvoiceSearch, CategorySearch


class Client(object):

    def __init__(self, domain, username, password, user_agent=None, token=None, login=True):
        self.BASE_URL = f'https://www.{domain}/rest/V1/'
        self.USER_CREDENTIALS = {
            'username': username,
            'password': password
        }
        self.ACCESS_TOKEN = token
        self.domain = domain
        self.user_agent = user_agent if user_agent else get_agent()

        if login:
            self.validate()

    @classmethod
    def from_json(cls, json_str):
        kwargs = json.loads(json_str)
        return cls(**kwargs)

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
        return OrderSearch(self)

    @property
    def invoices(self):
        return InvoiceSearch(self)

    @property
    def categories(self):
        return CategorySearch(self)

    @property
    def products(self):
        return ProductSearch(self)

    def authenticate(self) -> bool:
        """Request access token from the authentication endpoint."""
        endpoint = self.BASE_URL + 'integration/admin/token'
        payload = self.USER_CREDENTIALS
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': self.user_agent
        }

        print(f'Authenticating {payload["username"]} on {self.domain}...')
        response = requests.post(
            endpoint,
            json=payload,
            headers=headers
        )
        if response.ok:
            self.ACCESS_TOKEN = response.json()
        else:
            raise AuthenticationError(
                f'Failed to authenticate credentials: {response.json()}'
            )
        return self.validate()

    def search(self, endpoint: str):
        """Initializes and returns a SearchQuery object corresponding to the specified endpoint"""
        # Common endpoints are queried with SearchQuery subclasses containing endpoint-specific methods
        if endpoint.lower() == 'orders':
            return self.orders
        if endpoint.lower() == 'invoices':
            return self.invoices
        if endpoint.lower() == 'categories':
            return self.categories
        if endpoint.lower() == 'products':
            return self.products
        else:
            # Any other endpoint is queried with a general SearchQuery object
            return SearchQuery(endpoint=endpoint,
                               client=self)

    def validate(self):
        """Sends an authorized request to a standard API endpoint"""
        return self.request(self.BASE_URL + 'store/websites').status_code == 200

    def logout(self):
        """Deletes the access token"""
        self.ACCESS_TOKEN = None

    def request(self, url) -> requests.Response:
        """Sends a request with the access token. Used for all internal requests"""
        response = requests.get(url, headers=self.headers)
        if response.status_code == 401:
            # Invalid token, authenticate credentials and retry.
            self.authenticate()  # Invalid credentials will raise exception
            return self.request(url)
        elif response.status_code != 200:
            # Unknown error. Bad request url, nonexistent endpoint, etc.
            raise RuntimeError(
                "Request to {} failed with status code {} and message: \"{}\"".format(
                    url, response.status_code, response.json())
            )
        else:
            # Status Code is 200
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

    def url_for(self, endpoint):
        return self.BASE_URL + endpoint

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
