import os
import sys
import logging

import magento
from magento.utils import MagentoLogger, LoggerUtils
from magento.clients import Client, AuthenticationError

DOMAIN = 'website.com'
USERNAME = 'username'
PASSWORD = 'password'

PKG_LOG_NAME = MagentoLogger.PACKAGE_LOG_NAME
PKG_LOG_FILE = PKG_LOG_NAME + '.log'
PKG_LOG_PATH = os.path.abspath(PKG_LOG_FILE)

PKG_HANDLER = MagentoLogger.get_package_handler()
PKG_HANDLER_NAME = '{}__{}__{}'.format(
    MagentoLogger.PREFIX, MagentoLogger.PACKAGE_LOG_NAME, "WARNING"
)


def test_package_logger():
    logger.debug('Verifying package log file configuration...')
    pkg_logger = magento.logger
    pkg_log_files = LoggerUtils.get_log_files(pkg_logger)

    assert pkg_logger.name == PKG_LOG_NAME
    assert pkg_logger.log_file == PKG_LOG_FILE
    assert PKG_LOG_PATH in pkg_log_files
    assert os.path.exists(PKG_LOG_PATH)

    assert PKG_HANDLER in pkg_logger.handlers
    assert PKG_HANDLER.name == PKG_HANDLER_NAME
    assert PKG_HANDLER.baseFilename == PKG_LOG_PATH
    assert PKG_HANDLER.baseFilename in pkg_logger.log_files
    logger.debug('Package FileHandler is configured correctly')

    logger.debug('Verifying Package logger stdout configuration...')
    pkg_stream_handlers = LoggerUtils.get_stream_handlers(pkg_logger)
    assert len(pkg_stream_handlers) == 1  # Unsure about her...
    assert pkg_stream_handlers[0].level == logging.WARNING
    assert pkg_stream_handlers[0].name == PKG_HANDLER_NAME
    logger.debug('Package StreamHandler is configured correctly')


def test_client_logger_access(client: Client):
    """Test to make sure the Client attribute and method return the same object

    NOTE:
    client.logger -> MagentoLogger
    client.logger.logger -> logging.Logger
    """
    logger.debug('Verifying correct logger is returned from logger attribute and get_logger() method...')
    attr = client.logger.logger
    meth = client.get_logger().logger
    assert attr == meth
    logger.debug('Logger access is correct')
    return True


def test_client_logger_file_handlers(client: Client, log_file: str = None):
    logger.debug('Verifying client log file configuration...')
    client_logger = client.logger
    client_name = MagentoLogger.CLIENT_LOG_NAME.format(
        domain=client.domain.split('.')[0],
        username=client.USER_CREDENTIALS['username']
    )
    client_log_file = log_file if log_file else f'{client_name}.log'
    client_log_path = os.path.abspath(client_log_file)

    assert client_logger.name == client_name
    assert client_logger.log_file == client_log_file
    assert client_logger.log_path == client_log_path

    assert os.path.exists(client_logger.log_path)
    assert client_logger.log_path in client_logger.log_files

    logger.debug('Client log files are configured correctly')
    logger.debug('Verifying package handler is added to Client...')

    assert os.path.exists(PKG_LOG_PATH)
    assert PKG_LOG_PATH in client_logger.log_files  # Pkg logger added to all clients

    assert PKG_HANDLER in client_logger.handlers
    assert PKG_HANDLER.baseFilename in client_logger.log_files

    logger.debug('Log file configuration is correct')
    return True


def test_client_logger_stream_handlers(client: Client):
    logger.debug('Verifying client stdout configuration...')
    client_logger = client.logger
    client_name = MagentoLogger.CLIENT_LOG_NAME.format(
        domain=client.domain.split('.')[0],
        username=client.USER_CREDENTIALS['username']
    )
    client_stream_handlers = LoggerUtils.get_stream_handlers(client_logger)

    assert len(client_stream_handlers) == 1  # Should just be Client handler

    stream_handler_name = MagentoLogger.HANDLER_NAME.format(name=client_name, stdout_level="INFO")  # Default level
    stream_handler = client_stream_handlers[0]

    assert stream_handler.name == stream_handler_name
    assert stream_handler.level == logging.INFO

    logger.debug('Default stdout configuration is correct')
    logger.debug('Reconfiguring logger to use DEBUG stdout log level...')

    client_logger.setup_logger(stdout_level='DEBUG')
    client_stream_handlers = LoggerUtils.get_stream_handlers(client_logger)
    stream_handler_name = MagentoLogger.HANDLER_NAME.format(name=client_name, stdout_level="DEBUG")

    assert len(client_stream_handlers) == 1
    assert client_stream_handlers[0].level == logging.DEBUG
    assert client_stream_handlers[0].name == stream_handler_name

    logger.debug('Client logger level changed to DEBUG. Logging from Client...')
    client_logger.debug('If you can see this, log level was changed successfully')
    logger.debug("Changing client logger level back to INFO")

    client_logger.setup_logger(stdout_level="INFO")
    client_stream_handlers = LoggerUtils.get_stream_handlers(client_logger)
    stream_handler_name = stream_handler_name.replace("DEBUG", "INFO")  # From above

    assert len(client_stream_handlers) == 1
    assert client_stream_handlers[0].level == logging.INFO
    assert client_stream_handlers[0].name == stream_handler_name

    logger.debug('stdout log configuration is correct')
    return True


def test_log_file_change(client: Client):
    logger.debug('Verifying log file changes are accounted for...')
    client_logger = client.logger
    client_log_file_og = client_logger.log_file
    client_log_path_og = client_logger.log_path

    logger.debug(f'Current Log File: {client_log_file_og}')

    client_log_file_new = 'test_' + client_log_file_og
    client_logger.log_file = client_log_file_new

    logger.debug(f'Changed log file for client to {client_logger.log_file}')
    logger.debug('Setting up logger...')

    old_level = LoggerUtils.get_stream_handlers(client_logger)[0].name.split("__")[-1]  # StreamHandler.name = {}__{}__{stdout_level}
    client_logger.setup_logger(stdout_level=old_level)

    logger.debug(f'New logger set up. Should still be {old_level} for stdout, and writing only to the new log file')
    logger.debug('Verfying stdout configuration...')

    client_stream_handlers = LoggerUtils.get_stream_handlers(client_logger)

    assert len(client_stream_handlers) == 1
    assert client_stream_handlers[0].level == logging.getLevelName(old_level)

    logger.debug('Stdout configuration as expected.')
    logger.debug('Checking log file configuration...')

    if test_client_logger_file_handlers(client, client_log_file_new):
        logger.debug('New FileHandler set up correctly')

    logger.debug('Making sure old FileHandler is fully removed...')

    client_log_files = LoggerUtils.get_log_files(client_logger)
    magento_handlers = MagentoLogger.get_magento_handlers(client_logger)

    assert client_log_path_og not in client_log_files  # The old log file
    assert LoggerUtils.get_handler_by_log_file(client_logger, client_log_file_og) is None  # Handler should be removed too
    assert len([handler for handler in magento_handlers if isinstance(handler, logging.FileHandler)]) == 2
    logger.debug('Old FileHandler is fully removed')


def test_for_requests_logger(client: Client):
    import requests

    requests_logger = requests.urllib3.connectionpool.log
    requests_log_files = LoggerUtils.get_log_files(requests_logger)

    assert PKG_LOG_PATH in requests_log_files
    assert client.logger.log_path in requests_log_files
    logger.debug('The requests package logger is writing to both the Client and package log files')


if __name__ == '__main__':
    logger = MagentoLogger(
        name='logger_test',
        log_file='logger_test.log',
        stdout_level='DEBUG'
    )

    logger.debug('Beginning logger test')
    test_package_logger()

    logger.debug('Switching to Client logger for remaining tests...')

    client = Client(
        domain=DOMAIN,
        username=USERNAME,
        password=PASSWORD,
        login=False
    )

    logger.debug('Logging in to client...')

    try:
        client.authenticate()
        logger.debug('Client logged in')
        client.logger.info('Hello')  # Client loggers are set to "INFO" for console by default

    except AuthenticationError as e:
        logger.info('Failed to obtain an access token. Please ensure your credentials are correct')
        sys.exit(-1)

    test_client_logger_access(client)
    test_client_logger_file_handlers(client)
    test_client_logger_stream_handlers(client)
    test_log_file_change(client)
    test_for_requests_logger(client)

    logger.debug('All tests passed')
    sys.exit(0)
