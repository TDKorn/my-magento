from __future__ import annotations
import json
import copy
import pickle

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
            self.authenticate()

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

    def search(self, endpoint: str):
        """Initializes and returns a SearchQuery object corresponding to the specified endpoint"""
        if endpoint.lower() == 'orders':
            return self.orders
        if endpoint.lower() == 'invoices':
            return self.invoices
        if endpoint.lower() == 'categories':
            return self.categories
        if endpoint.lower() == 'products':
            return self.products
        # Any other endpoint is queried with a general SearchQuery object
        return SearchQuery(endpoint=endpoint, client=self)

    def authenticate(self) -> bool:
        """Request access token from the authentication endpoint."""
        endpoint = self.url_for('integration/admin/token')
        payload = self.USER_CREDENTIALS
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': self.user_agent
        }
        print(f'Authenticating {payload["username"]} on {self.domain}...')
        response = requests.post(
            url=endpoint,
            json=payload,
            headers=headers
        )
        if response.ok:
            print(f'Logged in to {payload["username"]}')
            self.ACCESS_TOKEN = response.json()
        else:
            raise AuthenticationError(
                f'Failed to authenticate credentials: {response.json()}'
            )
        return self.validate()

    def request(self, url) -> requests.Response:
        """Sends a request with the access token. Used for all internal requests"""
        response = requests.get(url, headers=self.headers)
        if response.status_code == 401:
            self.authenticate()  # Will raise exception if unsuccessful (won't recurse infinitely)
            return self.request(url)
        else:
            # Any other response, successful or not, will be returned; error handling is left to methods
            if response.status_code != 200:
                print(
                    "Request to {} failed with status code {} and message: \"{}\"".format(
                        url, response.status_code, response.json().get('message', 'None'))
                )
            return response

    def url_for(self, endpoint, scope=''):
        """Returns the appropriate url for the given endpoint and store scope"""
        if not scope:
            return self.BASE_URL + endpoint
        else:  # Must send POST/PUT requests to a scoped url for some updates
            return self.BASE_URL.replace('/V1', f'/{scope}/V1') + endpoint

    def validate(self):
        """Sends an authorized request to a standard API endpoint"""
        return self.request(self.url_for('store/websites')).status_code == 200

    @property
    def headers(self) -> {}:
        """Any time this is called, the token is validated"""
        return {
            'Authorization': f'Bearer {self.token}',
            'User-Agent': self.user_agent
        }

    @property
    def token(self) -> str:
        """Returns or generates access token"""
        if not self.ACCESS_TOKEN:
            self.authenticate()
        return self.ACCESS_TOKEN

    @classmethod
    def new(cls):
        return cls(
            input('Domain: '),
            input('Username: '),
            input('Password: '),
            user_agent=input('User Agent: ')
        )

    @classmethod
    def load(cls, pickle_bytes):
        return pickle.loads(pickle_bytes)

    def to_pickle(self, validate=False):
        if validate:
            try:
                self.validate()
            except AuthenticationError as e:
                raise e
        return pickle.dumps(self)

    @classmethod
    def from_json(cls, json_str):
        kwargs = json.loads(json_str)
        return cls(**kwargs)

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


class AuthenticationError(Exception):
    pass
