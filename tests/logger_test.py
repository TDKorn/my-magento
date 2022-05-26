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
    api.logger.debug('Logged in from {}'.format(
        os.path.abspath('logger_test.py'))
    )
    logger.debug('Client logged in.')

except AuthenticationError as e:
    logger.error(e)
    logger.debug('Failed to authenticate credentials. Test requires login.')
    sys.exit(-1)

logger.debug('Verifying correct logger is returned from logger attribute and get_logger() method...')
attr = api.logger.logger
meth = api.get_logger().logger
assert attr == meth

logger.debug('Checking handlers...')
handlers = [h for h in attr.handlers]
assert len(handlers) < 4

logger.debug('Checking file handlers...')
f_handlers = [f for f in handlers if isinstance(f, logging.FileHandler)]
assert len(f_handlers) == 2
f1, f2 = f_handlers


def fname_from_handler(f_handler):
    return os.path.basename(f_handler.baseFilename)


logger.debug('Checking log files...')
magento_log = MagentoLogger.PACKAGE_LOG_NAME + '.log'
client_log = MagentoLogger.CLIENT_LOG_NAME.format(
    DOMAIN=DOMAIN.split('.')[0],
    USERNAME=USERNAME
) + '.log'

assert magento_log in map(fname_from_handler, [f1, f2])
assert client_log in map(fname_from_handler, [f1, f2])
logger.debug('All tests passed')
sys.exit(0)
