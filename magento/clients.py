from __future__ import annotations
import json
import copy
import pickle
import requests

from .utils import MagentoLogger, get_agent
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
        self.user_agent = user_agent if user_agent else get_agent()
        self.logger = self.get_logger(log_level)

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
            raise AuthenticationError(self, response=response)

        self.logger.debug('Validating token...')
        try:
            self.validate()
        except AuthenticationError as e:
            raise AuthenticationError(self, msg='Token validation failed') from e

        self.logger.info('Logged in to {}'.format(payload["username"]))
        return True

    def request(self, url: str) -> requests.Response:
        """Sends a request with the access token. Used for all internal requests"""
        response = requests.get(url, headers=self.headers)
        if response.status_code == 401:
            self.logger.debug("Attempting to re-authenticate...")
            self.authenticate()  # Will raise AuthenticationError if unsuccessful (won't recurse infinitely)
            return self.request(url)

        if response.status_code != 200:  # All other responses are returned; errors are handled by methods
            self.logger.error("Request to {} failed with status code {} and message: \"{}\"".format(
                url, response.status_code, response.json().get('message', response.json()))
            )
        return response

    def url_for(self, endpoint, scope=''):
        """Returns the appropriate url for the given endpoint and store scope"""
        if not scope:
            return self.BASE_URL + endpoint
        else:   # Must send request to a scoped url for some updates
            return self.BASE_URL.replace('/V1', f'/{scope}/V1') + endpoint

    def validate(self) -> bool:
        """Sends an authorized request to a base API endpoint"""
        response = self.request(self.url_for('store/websites'))
        if response.status_code == 200:
            self.logger.debug("Token validated for {} on {}".format(
                self.USER_CREDENTIALS['username'], self.domain)
            )
            return True
        else:
            msg = "Token validation failed for {} on {}".format(
                self.USER_CREDENTIALS['username'], self.domain
            )
            raise AuthenticationError(self, msg=msg, response=response)

    def get_logger(self, level='INFO') -> MagentoLogger:
        """Retrieve the MagentoLogger associated with the current username/domain combination"""
        log_name = MagentoLogger.CLIENT_LOG_NAME.format(
            DOMAIN=self.domain.split('.')[0],
            USERNAME=self.USER_CREDENTIALS['username']
        )
        return MagentoLogger(  # Note that there is one-way access to the logger
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
            self.validate()
        return pickle.dumps(self)

    def to_json(self, validate=False) -> str:
        """Validates and saves login credentials for this domain"""
        if validate:
            self.validate()
        data = {    # Add more to this if you want!
            'domain': self.domain,
            'user_agent': self.user_agent,
            'token': self.token,
            'log_level': self.logger.logger.level
        }
        data.update(self.USER_CREDENTIALS)
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str) -> Client:
        kwargs = json.loads(json_str)
        return cls(**kwargs)


class AuthenticationError(Exception):

    DEFAULT_MSG = 'Failed to authenticate credentials. '

    def __init__(self, client: Client, msg=None, response: requests.Response = None):
        self.message = msg if msg else AuthenticationError.DEFAULT_MSG
        self.logger = client.logger

        if response is not None:
            self.parse(response)

        self.logger.error(self.message)
        super().__init__(self.message)

    def parse(self, response: requests.Response) -> None:
        """Parses the error message from the response, including message parameters when available"""
        msg = response.json().get('message')
        errors = response.json().get('errors')

        if msg:
            self.message += ' ' + '\n' + f'Response: {msg}'

        if errors:
            for error in errors:
                err_msg = error['message']
                err_params = error.get('parameters')

                if err_params:
                    for param in err_params:
                        err_msg = err_msg.replace(f'%{param}', err_params[param])

                self.message += err_msg + '\n'
