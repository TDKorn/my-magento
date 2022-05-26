from __future__ import annotations
import json
import copy
import pickle
import requests

from . import utils
from .search import SearchQuery, OrderSearch, ProductSearch, InvoiceSearch, CategorySearch


class Client(object):

    def __init__(self, domain, username, password, user_agent=None, token=None, log_level='INFO', login=True):
        self.BASE_URL = f'https://www.{domain}/rest/V1/'
        self.USER_CREDENTIALS = {
            'username': username,
            'password': password
        }
        self.ACCESS_TOKEN = token
        self.domain = domain
        self.user_agent = user_agent if user_agent else utils.get_agent()
        self.logger = self.get_logger(
            level=log_level
        )
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

    def search(self, endpoint: str) -> SearchQuery:
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

    def authenticate(self) -> bool:
        """Request access token from the authentication endpoint."""
        endpoint = self.url_for('integration/admin/token')
        payload = self.USER_CREDENTIALS
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': self.user_agent
        }
        self.logger.info(f'Authenticating {payload["username"]} on {self.domain}...')
        response = requests.post(
            url=endpoint,
            json=payload,
            headers=headers
        )
        if response.ok:
            self.ACCESS_TOKEN = response.json()
        else:
            msg = f'Failed to authenticate credentials: {response.json()}'
            self.logger.debug(msg)
            raise AuthenticationError(msg)

        if self.validate():
            self.logger.info('Logged in to {}'.format(payload["username"]))
            return True

        raise AuthenticationError()  # validate() will have already logged the error msg

    def request(self, url: str) -> requests.Response:
        """Sends a request with the access token. Used for all internal requests"""
        response = requests.get(url, headers=self.headers)
        if response.status_code == 401:
            self.authenticate()  # Will raise exception if unsuccessful (won't recurse infinitely)
            return self.request(url)
        else:
            # Any other response, successful or not, will be returned; error handling is left to methods
            if response.status_code != 200:
                self.logger.info(
                    "Request to {} failed with status code {} and message: \"{}\"".format(
                        url, response.status_code, response.json().get('message', response.json())
                    )
                )
            return response

    def url_for(self, endpoint, scope=''):
        """Returns the appropriate url for the given endpoint and store scope"""
        if not scope:
            return self.BASE_URL + endpoint
        else:   # Must send request to a scoped url for some updates
            return self.BASE_URL.replace('/V1', f'/{scope}/V1') + endpoint

    def validate(self) -> bool:
        """Sends an authorized request to a standard API endpoint"""
        response = self.request(self.url_for('store/websites'))
        if response.status_code == 200:
            self.logger.debug("Client validated for {} on {}".format(
                self.USER_CREDENTIALS['username'], self.domain))
            return True
        else:
            message = response.json().get('message', response.json())
            self.logger.error(
                "Client validation failed for {} on {}\nResponse: {}".format(
                    self.USER_CREDENTIALS['username'], self.domain, message
                )
            )
            return False

    def get_logger(self, level='INFO') -> utils.MagentoLogger:
        """
        Retrieve the MagentoLogger for this Client. Logger names are of the form "<username>_<domain>"

        :return:  the MagentoLogger associated with the current user/domain combination

        """
        log_name = self.USER_CREDENTIALS['username'] + '_' + self.domain.split('.')[0]
        return utils.MagentoLogger(
            name=log_name,
            log_file=log_name + '.log',
            stdout_level=level
        )

    @property
    def headers(self) -> dict:
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
    def new(cls) -> Client:
        return cls(
            input('Domain: '),
            input('Username: '),
            input('Password: '),
            user_agent=input('User Agent: ')
        )

    @classmethod
    def load(cls, pickle_bytes) -> Client:
        return pickle.loads(pickle_bytes)

    def to_pickle(self, validate=False) -> bytes:
        """Validates credentials (optional) and returns the Client object as a pickle string"""
        if validate:
            if not self.validate():
                raise AuthenticationError(
                    'Failed to validate credentials'
                )
        return pickle.dumps(self)

    def to_json(self, validate=False) -> str:
        """Validates and saves login credentials for this domain"""
        data = copy.deepcopy(self.USER_CREDENTIALS)
        if validate:
            if not self.validate():
                raise AuthenticationError('Failed to validate credentials')
        data.update(
            {  # Add more to this if you want!
                'username': self.USER_CREDENTIALS['username'],
                'password': self.USER_CREDENTIALS['password'],
                'domain': self.domain,
                'user_agent': self.user_agent,
                'token': self.token
            }
        )
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str) -> Client:
        kwargs = json.loads(json_str)
        return cls(**kwargs)


class AuthenticationError(Exception):
    pass
