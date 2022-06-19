MagentoLogger
====

Logging class used within the package

:cvar PREFIX:           hardcoded prefix to use in log messages
:cvar PACKAGE_LOG_NAME: the default name for the package logger
:cvar CLIENT_LOG_NAME:  the default format for the client logger name
:cvar LOG_MESSAGE:      the default format for the message component of log messages.
                            (Use magento.logger.LOG_MESSAGE for easy access)
:cvar FORMATTER:        the default logging format
:cvar HANDLER_NAME      the default format for the names of handlers created by this package




====

    PREFIX = "MyMagento"
    PACKAGE_LOG_NAME = "my-magento"
    CLIENT_LOG_NAME = "{domain}_{username}"
    HANDLER_NAME = '{}__{}__{}'.format(PREFIX, '{name}', '{stdout_level}')
    LOG_MESSAGE = "|[ {pfx} | {name} ]|:  {message}".format(
        pfx=PREFIX, name="{name}", message="{message}"
    )
    FORMATTER = logging.Formatter(
        fmt="%(asctime)s %(levelname)-5s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    def __init__(self, name: str, log_file: str = None, stdout_level: Union[int | str] = 'INFO',
                 log_requests: bool = True):
        """Initialize the logger

        Each Client object corresponds to a unique username/domain combination, which is used to attach it to its
        associated MagentoLogger and log file, allowing all activity across all endpoints to be tracked.
        A package logger exists as well, which logs all activity from the package.
        All log files have their log level set to DEBUG

        :param name: logger name
        :param log_file: log file name; default is {name}.log
        :param stdout_level: logging level for stdout logger; default is "INFO" (which is also logging.INFO and 10)
        :param log_requests: set to True to add logging from the requests package logger
        """
        self.name = name
        self.logger = None
        self.handler_name = None
        self.log_file = log_file if log_file else f'{self.name}.log'
        self.setup_logger(stdout_level, log_requests=log_requests)

    def setup_logger(self, stdout_level: Union[int | str] = 'INFO', log_requests: bool = True) -> bool:
        """Configures a logger and assigns it to the `logger` attribute.

        :cvar MagentoLogger.HANDLER_NAME: the string used to format names of all FileHandler and StreamHandler objects
        :param stdout_level: logging level to use for logging to console
        :param log_requests: set to True to add logs from the requests package (ie. API call logging)
        :attr handler_name: name for all handlers
        """
        logger = logging.getLogger(self.name)
        handler_map = LoggerUtils.map_handlers_by_name(logger)
        log_files = LoggerUtils.get_log_files(logger)
        name = self.name
        self.handler_name = f'{self.HANDLER_NAME}'
Traceback (most recent call last):
  File "C:\Python310\lib\code.py", line 90, in runcode
    exec(code, self.locals)
  File "<input>", line 1, in <module>
  File "<input>", line 28, in MagentoLogger
NameError: name 'Union' is not defined
import os
import sys
import logging
import requests
from typing import Union, List, Type
from logging import Logger, FileHandler, StreamHandler, Handler
PREFIX = "MyMagento"
HANDLER_NAME = '{}__{}__{}'.format(PREFIX, '{name}', '{stdout_level}')
print(HANDLER_NAME)
MyMagento__{name}__{stdout_level}
LOG_MESSAGE = "|[ {pfx} | {name} ]|:  {message}".format(
        pfx=PREFIX, name="{name}", message="{message}"
    )
print(LOG_MESSAGE)
|[ MyMagento | {name} ]|:  {message}
PACKAGE_LOG_NAME = "my-magento"
CLIENT_LOG_NAME = "{domain}_{username}"
print(LOG_MESSAGE.format(
    name=PACKAGE_LOG_NAME, message="Pack Logger"
))
|[ MyMagento | my-magento ]|:  Pack Logger
PACKAGE_LOG_NAME = "my-magento"
CLIENT_LOG_NAME = "{domain}_{username}"
print(LOG_MESSAGE.format(
    name=PACKAGE_LOG_NAME, message="Package Logger"
))
print(LOG_MESSAGE.format(
    name=CLIENT_LOG_NAME, message="Package Logger"
))
|[ MyMagento | my-magento ]|:  Package Logger
|[ MyMagento | {domain}_{username} ]|:  Package Logger
PACKAGE_LOG_NAME = "my-magento"
CLIENT_LOG_NAME = "{domain}_{username}".format(
    domain="CatStore64", username="luigi"
)
print(LOG_MESSAGE.format(
    name=PACKAGE_LOG_NAME, message="Package Logger"
))
print(LOG_MESSAGE.format(
    name=CLIENT_LOG_NAME, message="CLIENT Logger"
))
|[ MyMagento | my-magento ]|:  Package Logger
|[ MyMagento | CatStore64_luigi ]|:  CLIENT Logger
PACKAGE_LOG_NAME = "my-magento"
CLIENT_LOG_NAME = "{domain}_{username}".format(
    domain="CatStore64", username="luigi"
)
print(LOG_MESSAGE.format(
    name=PACKAGE_LOG_NAME, message="Package Logger"
))
print(LOG_MESSAGE.format(
    name=CLIENT_LOG_NAME, message="Client Logger"
))
|[ MyMagento | my-magento ]|:  Package Logger
|[ MyMagento | CatStore64_luigi ]|:  Client Logger
```