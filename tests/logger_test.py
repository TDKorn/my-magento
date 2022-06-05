import os
import sys
import logging

from magento.utils import MagentoLogger
from magento.clients import Client, AuthenticationError

DOMAIN = 'website.com'
USERNAME = 'username'
PASSWORD = 'password'

logger = MagentoLogger(
    name='logger_test',
    log_file='logger_test.log',
    stdout_level='DEBUG'
)

logger.debug('Beginning logger test')
logger.debug('Logging in to client...')
try:
    api = Client(
        domain=DOMAIN,
        username=USERNAME,
        password=PASSWORD
    )

except AuthenticationError as e:
    logger.info('Failed to obtain an access token. Please ensure your credentials are corred')
    sys.exit(-1)

logger.debug('Client logged in.')
api.logger.debug('Using Client logger to log to {}'.format(__file__))  # Is that a weird test...?

logger.debug('Verifying correct logger is returned from logger attribute and get_logger() method...')
attr = api.logger.logger
meth = api.get_logger().logger
assert attr == meth

logger.debug('Verifying magento and Client log FileHandlers are present...')
magento_log = MagentoLogger.PACKAGE_LOG_NAME + '.log'
client_log = MagentoLogger.CLIENT_LOG_NAME.format(
    DOMAIN=DOMAIN.split('.')[0],
    USERNAME=USERNAME) + '.log'


def get_filehandlers(logger: logging.Logger):
    """Get all the FileHandlers handling a logger"""
    return [handler for handler in logger.handlers if isinstance(handler, logging.FileHandler)]


def get_logfiles(logger):
    """Get the log file paths from all FileHandlers of a logger"""
    return [handler.baseFilename for handler in get_filehandlers(logger)]


assert os.path.abspath(magento_log) in get_logfiles(api.logger.logger)
assert os.path.abspath(client_log) in get_logfiles(api.logger.logger)
logger.debug('The Client is writing to both the Client and package log files ')

requests_logger = logging.getLogger('urllib3.connectionpool')
assert os.path.abspath(magento_log) in get_logfiles(requests_logger)
assert os.path.abspath(client_log) in get_logfiles(requests_logger)
logger.debug('The requests package logger is writing to both the Client and package log files')

logger.debug('All tests passed')
sys.exit(0)
