import os
import sys
import logging
import requests

from typing import Union, List, Type
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
    """Logging class used within the package

    :cvar PREFIX:           hardcoded prefix to use in log messages
    :cvar PACKAGE_LOG_NAME: the default name for the package logger
    :cvar CLIENT_LOG_NAME:  the default format for the client logger name
    :cvar LOG_MESSAGE:      the default format for the message component of log messages.
                            (Use magento.logger.LOG_MESSAGE for easy access)
    :cvar FORMATTER:        the default logging format
    :type FORMATTER:        logging.Formatter
    :cvar HANDLER_NAME      the default format for the names of handlers created by this package
    """

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

    def __init__(self, name: str, log_file: str = None, stdout_level: Union[int | str] = 'INFO', log_requests: bool = True):

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

        :param stdout_level: logging level to use for logging to console
        :param log_requests: set to True to add logs from the requests package (ie. API call logging)
        """
        logger = logging.getLogger(self.name)
        log_files = LoggerUtils.get_log_files(logger)
        handler_map = LoggerUtils.map_handlers_by_name(logger)

        self.handler_name = MagentoLogger.HANDLER_NAME.format(
            name=self.name, stdout_level=stdout_level
        )
        if self.handler_name in handler_map['stream'] and self.handler_name in handler_map['file']:
            if self.log_path in log_files:
                self.logger = logger  # Log levels and log files are correct
                return True

        if self.handler_name not in handler_map['stream']:
            if len(handler_map['stream']) > 0:
                self.clear_magento_handlers(logger, handler_type=StreamHandler)
            # Resetting ensures only the desired level is logged to console
            stdout_handler = StreamHandler(stream=sys.stdout)
            stdout_handler.setFormatter(MagentoLogger.FORMATTER)
            stdout_handler.name = self.handler_name
            stdout_handler.setLevel(stdout_level)
            logger.addHandler(stdout_handler)

        # Remove all FileHandlers created by this package (except handler for magento.log)
        if self.handler_name not in handler_map['file'] or self.log_path not in log_files:
            if len(handler_map['file']) > 0:
                self.clear_magento_file_handlers(logger)
            f_handler = FileHandler(self.log_file)
            f_handler.setFormatter(MagentoLogger.FORMATTER)
            f_handler.name = self.handler_name
            f_handler.setLevel("DEBUG")
            logger.addHandler(f_handler)

        if log_requests:
            f_handler = LoggerUtils.get_handler_by_log_file(logger, self.log_file)  # In case it wasn't just created
            MagentoLogger.add_request_logging(f_handler)

        if self.name != MagentoLogger.PACKAGE_LOG_NAME:  # All clients have the handler added to them
            pkg_handler = MagentoLogger.get_package_handler()   # For writing to {PACKAGE_LOG_NAME}.log
            logger.addHandler(pkg_handler)
            f_handler = LoggerUtils.get_handler_by_log_file(logger, self.log_file)
            MagentoLogger.add_request_logging(f_handler)

        if self.name != MagentoLogger.PACKAGE_LOG_NAME:
            pkg_handler = MagentoLogger.get_package_handler()
            logger.addHandler(pkg_handler)  # For writing to {PACKAGE_LOG_NAME}.log

        logger.setLevel(logging.DEBUG)
        self.logger = logger
        return True

    def format_msg(self, msg: str) -> str:
        """Formats MagentoLogger.LOG_MESSAGE using the specified message"""
        return MagentoLogger.LOG_MESSAGE.format(
            name=self.name,
            message=msg
        )

    def debug(self, msg):
        """Formats MagentoLogger.LOG_MESSAGE with the specified message, then logs it with Logger.debug()"""
        return self.logger.debug(
            self.format_msg(msg)
        )

    def info(self, msg):
        """Formats MagentoLogger.LOG_MESSAGE with the specified message, then logs it with Logger.info()"""
        return self.logger.info(
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

    def critical(self, msg):
        """Formats MagentoLogger.LOG_MESSAGE with the specified message, then logs it with Logger.critical()"""
        return self.logger.critical(
            self.format_msg(msg)
        )

    @property
    def handlers(self):
        return self.logger.handlers

    @property
    def handler_names(self):
        return LoggerUtils.get_handler_names(self.logger)

    @property
    def handler_map(self):
        return LoggerUtils.map_handlers_by_name(self.logger)

    @property
    def file_handlers(self):
        return LoggerUtils.get_file_handlers(self.logger)

    @property
    def stream_handlers(self):
        return LoggerUtils.get_stream_handlers(self.logger)

    @property
    def log_files(self):
        return LoggerUtils.get_log_files(self.logger)

    @property
    def log_path(self):
        return os.path.abspath(self.log_file)

    @staticmethod
    def get_magento_handlers(logger):
        return [handler for handler in logger.handlers if MagentoLogger.owns_handler(handler)]

    @staticmethod
    def clear_magento_handlers(logger: Logger, handler_type: Union[Type[FileHandler] | Type[StreamHandler]], clear_pkg: bool = False) -> None:
        """Clear all handlers from a logger that were created by MagentoLogger

        :param logger: any logger
        :param handler_type: the logging handler type to check for and remove
        :param clear_pkg: if True, will delete the package handler for writing to my-magento.log | (Default is False)
        """
        for handler in MagentoLogger.get_magento_handlers(logger):
            if type(handler) == handler_type:
                if clear_pkg is True or handler != MagentoLogger.get_package_handler():
                    logger.removeHandler(handler)  # Either remove all handlers, or all but pkg handler

    @staticmethod
    def clear_magento_file_handlers(logger: Logger, clear_pkg: bool = False):
        return MagentoLogger.clear_magento_handlers(logger, FileHandler, clear_pkg)

    @staticmethod
    def clear_magento_stdout_handlers(logger: Logger, clear_pkg: bool = False):
        return MagentoLogger.clear_magento_handlers(logger, StreamHandler, clear_pkg)

    @staticmethod
    def owns_handler(handler: Handler):
        """Checks if a handler is a Stream/FileHandler from this package or not"""
        try:  # Match handler name to MagentoLogger.HANDLER_NAME format
            prefix, name, stdout_level = handler.name.split('__')
            return prefix == MagentoLogger.PREFIX
        except:  # Wrong format or not set
            return False

    @staticmethod
    def get_package_handler() -> FileHandler:
        """Returns the FileHandler object that writes to the magento.log file"""
        pkg_handlers = logging.getLogger(MagentoLogger.PACKAGE_LOG_NAME).handlers
        for handler in pkg_handlers:
            if isinstance(handler, FileHandler):
                if handler.baseFilename == os.path.abspath(MagentoLogger.PACKAGE_LOG_NAME + '.log'):
                    return handler

    @staticmethod
    def add_request_logging(handler: Union[FileHandler | StreamHandler]):
        """Adds the specified handler to the requests package logger, allowing for easier debugging of API calls"""
        if type(handler) not in (FileHandler, StreamHandler):
            raise TypeError(f"Parameter handler must be of type {FileHandler} or {StreamHandler}")

        req_logger = requests.urllib3.connectionpool.log
        req_logger.setLevel("DEBUG")
        if handler in req_logger.handlers:
            return True  # Already added

        if type(handler) is FileHandler:
            if handler.baseFilename not in LoggerUtils.get_log_files(req_logger):
                req_logger.addHandler(handler)  # Might be same handler new file (or level)

        elif type(handler) is StreamHandler:
            stdout_names = LoggerUtils.map_handlers_by_name(req_logger)['stream']
            if handler.name not in stdout_names: # Might be same handler new level
                req_logger.addHandler(handler)

        return True


AGENTS = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36']


def get_agents() -> list:
    """Scrapes a list of user agents. Returns a default list if the scrape fails."""
    if (response := requests.get('https://www.whatismybrowser.com/guides/the-latest-user-agent/chrome')).ok:
        section = response.text.split('<h2>Latest Chrome on Windows 10 User Agents</h2>')[1]
        raw_agents = section.split('code\">')[1:]
        agents = [agent.split('<')[0] for agent in raw_agents]
        for a in agents:
            if a not in AGENTS:
                AGENTS.append(a)
    # If function fails, will still return the hardcoded list
    return AGENTS


def get_agent(index=0) -> str:
    """Returns a single user agent string from the specified index of the AGENTS list"""
    return get_agents()[index]  # Specify index only if you hardcode more than 1


def get_package_file_handler():
    return MagentoLogger.get_package_handler()
