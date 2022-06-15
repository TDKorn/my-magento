import os
import sys
import logging
import requests

from typing import Union, List
from logging import Logger, FileHandler, StreamHandler, Handler


class ItemManager:

    def __init__(self, items=None):
        self.items = items if items else []

    def add(self, item):
        if item not in self.items:
            self.items.append(item)

    def get_attrs(self, attr):
        return [getattr(item, attr, 0) for item in self.items]

    def sum_attrs(self, attr):
        return sum(self.get_attrs(attr))


class LoggerUtils:
    """Utility class that simplifies access to logger handler info"""

    @staticmethod
    def get_handler_names(logger) -> List[str]:
        """Get all handler names"""
        return [handler.name for handler in logger.handlers]

    @staticmethod
    def get_stream_handlers(logger: Logger) -> List[Handler]:
        """Get all the StreamHandlers of the current logger (NOTE: StreamHandler subclasses excluded)"""
        return [handler for handler in logger.handlers if type(handler) == StreamHandler]

    @staticmethod
    def get_file_handlers(logger: Logger) -> List[FileHandler]:
        """Get all the FileHandlers of the current logger"""
        return [handler for handler in logger.handlers if isinstance(handler, FileHandler)]

    @staticmethod
    def get_log_files(logger: Logger) -> List[str]:
        """Get the log file paths from all FileHandlers of a logger"""
        return [handler.baseFilename for handler in LoggerUtils.get_file_handlers(logger)]

    @staticmethod
    def get_handler_by_log_file(logger: Logger, log_file: str) -> FileHandler:
        """Returns the FileHandler logging to the specified file, given it exists"""
        for handler in LoggerUtils.get_file_handlers(logger):
            if os.path.basename(handler.baseFilename) == log_file:
                return handler

    @staticmethod
    def clear_handlers(logger: Logger) -> bool:
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
        return logger.handlers == []

    @staticmethod
    def clear_stream_handlers(logger: Logger) -> bool:
        """Removes all StreamHandlers from a logger"""
        for handler in LoggerUtils.get_stream_handlers(logger):
            logger.removeHandler(handler)
        return LoggerUtils.get_stream_handlers(logger) == []

    @staticmethod
    def clear_file_handlers(logger: Logger) -> bool:
        """Removes all FileHandlers from a logger"""
        for handler in LoggerUtils.get_file_handlers(logger):
            logger.removeHandler(handler)
        return LoggerUtils.get_file_handlers(logger) == []

    @staticmethod
    def map_handlers_by_name(logger: Logger):
        """Map the handlers of a logger first by type, and then by their name

        FileHandlers are mapped to both their handlers and log file, while StreamHandlers are just mapped to the handler
        Handlers without a name will be skipped, because look at the method name (:
        """
        mapping = {
            'stream': {},
            'file': {}
        }
        for stream_handler in LoggerUtils.get_stream_handlers(logger):
            if stream_handler.name:
                mapping['stream'][stream_handler.name] = stream_handler

        for file_handler in LoggerUtils.get_file_handlers(logger):
            if file_handler.name:
                entry = mapping['file'].setdefault(file_handler.name, {})
                entry['handler'] = file_handler
                entry['file'] = file_handler.baseFilename

        return mapping


class MagentoLogger:
    PACKAGE_LOG_NAME = "magento"
    CLIENT_LOG_NAME = "{DOMAIN}_{USERNAME}"
    PREFIX = "MyMagento"
    # Use magento.logger.LOG_MESSAGE for easy access
    LOG_MESSAGE = "|[ {pfx} | {name} ]|:  {message}".format(
        pfx=PREFIX, name="{name}", message="{message}"
    )
    FORMATTER = logging.Formatter(
        fmt="%(asctime)s %(levelname)-5s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    def __init__(self, name: str, log_file: str = '', stdout_level: Union[int, str] = 'INFO'):
        """Logging class used within the package. An instance is attached to every Client upon object initialization.

        Currently, a single Client object is created for each username/domain combination, and this same Client object
        is passed between all wrapper classes in the package. Since a logger/log file is uniquely associated with a
        particular user, this allows all activity, across all endpoints, to be logged every time that user logs in
        (Please don't be creepy with that)
        All activity from the package, regardless of user, will be logged to the central "magento.log" package log file

        NOTE: Logging level for stdout logging can be set (default is "INFO") but log files are forced to use "DEBUG"

        :param name: logger name
            :var MagentoLogger.CLIENT_LOG_NAME:  the default client logger name
            :var MagentoLogger.PACKAGE_LOG_NAME: the default package logger name

        :param log_file: log file name; default is {name}.log
        :param stdout_level: logging level for stdout logger; default is "INFO" (which is also logging.INFO and 10)
        """
        self.name = name
        self.logger = self.setup_logger(
            log_file=log_file,
            stdout_level=stdout_level
        )

    def setup_logger(self, log_file: str = '', stdout_level: Union[int, str] = 'INFO'):
        """Configures and returns a logger. Uses existing loggers if possible"""
        logger = logging.getLogger(self.name)
        stdout_name = f'{self.name}_stdoutLogger'
        for handler in logger.handlers:
            if handler.name == stdout_name:
                return logger

        stdout_handler = logging.StreamHandler(stream=sys.stdout)
        stdout_handler.name = stdout_name
        stdout_handler.setLevel(stdout_level)
        stdout_handler.setFormatter(MagentoLogger.FORMATTER)

        if not log_file:
            log_file = f'{self.name}.log'

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(MagentoLogger.FORMATTER)

        logger.setLevel(logging.DEBUG)
        logger.addHandler(stdout_handler)
        logger.addHandler(file_handler)

        MagentoLogger.add_request_logging(file_handler)

        if self.name != MagentoLogger.PACKAGE_LOG_NAME:
            logger.addHandler(MagentoLogger.get_package_handler())

        return logger

    def format_msg(self, msg: str) -> str:
        """Formats MagentoLogger.LOG_MESSAGE using the specified message"""
        return MagentoLogger.LOG_MESSAGE.format(
            name=self.name,
            message=msg
        )

    def info(self, msg):
        """Formats MagentoLogger.LOG_MESSAGE with the specified message, then logs it with Logger.info()"""
        return self.logger.info(
            self.format_msg(msg)
        )

    def debug(self, msg):
        """Formats MagentoLogger.LOG_MESSAGE with the specified message, then logs it with Logger.debug()"""
        return self.logger.debug(
            self.format_msg(msg)
        )

    def error(self, msg):
        """Formats MagentoLogger.LOG_MESSAGE with the specified message, then logs it with Logger.error()"""
        return self.logger.error(
            self.format_msg(msg)
        )

    def warning(self, msg):
        """Formats MagentoLogger.LOG_MESSAGE with the specified message, then logs it with Logger.warning()"""
        return self.logger.warning(
            self.format_msg(msg)
        )

    @staticmethod
    def get_package_handler() -> logging.FileHandler:
        """Returns the FileHandler object that writes to the magento.log file"""
        pkg_handlers = logging.getLogger(MagentoLogger.PACKAGE_LOG_NAME).handlers
        for handler in pkg_handlers:
            if isinstance(handler, logging.FileHandler):
                return handler

    @staticmethod
    def add_request_logging(handler: Union[logging.FileHandler, logging.StreamHandler]):
        """Adds the specified handler to the requests package logger, allowing for easier debugging of API calls"""
        req_logger = logging.getLogger('urllib3.connectionpool')
        req_logger.setLevel(logging.DEBUG)
        if handler not in req_logger.handlers:
            req_logger.addHandler(handler)



AGENTS = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36']


def get_agents() -> list:
    """Scrapes a list of user agents. Returns a default list if the scrape fails."""
    if (response := requests.get('https://www.whatismybrowser.com/guides/the-latest-user-agent/chrome')).ok:
        section = response.text.split('<h2>Latest Chrome on Windows 10 User Agents</h2>')[1]
        raw_agents = section.split('code\">')[1:]
        agents = [agent.split('<')[0] for agent in raw_agents]
        for a in agents:
            if a not in AGENTS:
                AGENTS.append(a)
    # If function fails will return the hardcoded list
    return AGENTS


def get_agent() -> str:
    """Returns a single user agent string"""
    return get_agents()[0]
