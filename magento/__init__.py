from . import clients
from . import search
from . import models
from . import utils
from . import exceptions
import os

__version__ = "2.1.3"

Client = clients.Client
logger = utils.MagentoLogger(
    name=utils.MagentoLogger.PACKAGE_LOG_NAME,
    log_file=utils.MagentoLogger.PACKAGE_LOG_NAME + '.log',
    stdout_level='WARNING'  # Clients will log to console
)


def get_api(**kwargs) -> Client:
    """Initialize a :class:`~.Client` using credentials stored in environment variables

    Any valid :class:`~.Client` kwargs can be used in addition to and/or instead of environment variables

    **Usage**::

      import magento

      api = magento.get_api()

    :param kwargs: any valid kwargs for :class:`~.Client`
    :raises ValueError: if login credentials are missing
    """
    credentials = {
        'domain': kwargs.get('domain', os.getenv('MAGENTO_DOMAIN')),
        'username': kwargs.get('username', os.getenv('MAGENTO_USERNAME')),
        'password': kwargs.get('password', os.getenv('MAGENTO_PASSWORD')),
        'local': kwargs.get('local', False),
    }
    if bad_keys := [key for key in credentials if credentials[key] is None]:
        raise ValueError(f'Missing login credentials for {bad_keys}')
    else:
        return Client.from_dict(credentials)


logger.debug('Initialized MyMagento')
