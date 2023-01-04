from __future__ import annotations
from typing import Union, Optional, TYPE_CHECKING
import requests

if TYPE_CHECKING:
    from . import Client


class MagentoError(Exception):

    """Base exception class for error responses returned by the Magento API

    :cvar DEFAULT_MSG: default exception message to use if a message isn't provided
    """

    DEFAULT_MSG = 'An error occurred while processing the request.'

    def __init__(self, client: Client, msg: Optional[str] = None, response: Optional[requests.Response] = None):
        """Log and raise a MagentoError

        :param client: an initialized :class:`~.Client` object
        :param msg: optional exception message; prepended to the error message of the response (if provided).
        :param response: optional response to :meth:`parse` an error message from
        """
        self.message = msg if msg else self.DEFAULT_MSG
        self.logger = client.logger

        if response is not None:
            self.message += '\n' + self.parse(response)

        self.logger.error(self.message)
        super().__init__(self.message)

    @staticmethod
    def parse(response: Union[requests.Response, dict]) -> str:
        """Parses the error message from the response, including message parameters when available

        :param response: a bad response returned by the Magento API
        """
        if isinstance(response, requests.Response):
            response = response.json()

        message = response.get('message', '')
        params = response.get('parameters')
        errors = response.get('errors')

        if message:
            message = f'Message: "{message}"'

        if errors:
            for error in errors:
                err_msg = error['message']
                err_params = error.get('parameters')

                if err_params:
                    for param in err_params:
                        err_msg = err_msg.replace(f'%{param}', err_params[param])

                message += '\n' + err_msg

        if params:
            if isinstance(params, dict):
                for param in params:  # Same format as error params
                    message = message.replace(f'%{param}', params[param])

            else:  # List of param values
                for i in range(len(params)):  # Message parameters use %{index}, starting from 1
                    message = message.replace(f'%{i+1}', params[i])

        return message


class AuthenticationError(MagentoError):

    """Exception class for errors when trying to :meth:`~.authenticate` a :class:`~.Client`"""

    DEFAULT_MSG = 'Failed to authenticate credentials.'

    def __init__(self, client: Client, msg: Optional[str] = None, response: Optional[requests.Response] = None):
        super().__init__(client, msg, response)
