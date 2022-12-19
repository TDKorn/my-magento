from magento import Client
import requests


class MagentoError(Exception):

    """Base exception class for error responses returned by the Magento API"""

    DEFAULT_MSG = 'An error occurred while processing the request.'  #: The default exception message

    def __init__(self, client: Client, msg=None, response: requests.Response = None):
        self.message = msg if msg else self.DEFAULT_MSG
        self.logger = client.logger

        if response is not None:
            self.parse(response)

        self.logger.error(self.message)
        super().__init__(self.message)

    def parse(self, response: requests.Response) -> None:
        """Parses the error message from the response, including message parameters when available

        :param response: a bad response returned by the Magento API
        """
        msg = response.json().get('message')
        errors = response.json().get('errors')

        if msg:
            self.message += '\n' + f'Response: {msg}'

        if errors:
            for error in errors:
                err_msg = error['message']
                err_params = error.get('parameters')

                if err_params:
                    for param in err_params:
                        err_msg = err_msg.replace(f'%{param}', err_params[param])

                self.message += err_msg + '\n'


class AuthenticationError(MagentoError):

    DEFAULT_MSG = 'Failed to authenticate credentials.'

    def __init__(self, client: Client, msg=None, response: requests.Response = None):
        super().__init__(client, msg, response)
