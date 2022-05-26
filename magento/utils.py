import sys
import logging
import requests


class ItemManager:

    def __init__(self):
        self.items = []

    def add(self, item):
        if item not in self.items:
            self.items.append(item)

    def get_attrs(self, attr):
        return [getattr(item, attr, 0) for item in self.items]

    def sum_attrs(self, attr):
        return sum(self.get_attrs(attr))


AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36',
]


def get_agents() -> []:
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


class MagentoLogger:

    FORMATTER = logging.Formatter(
        fmt="%(asctime)s %(levelname)-5s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    def __init__(self, name, log_file='', level=logging.INFO):
        """
        The logger used for this package. Mostly taken from the PyCloudLogger class in my other repo (you should check it out, it's useful 😉)
        (https://github.com/TDKorn/icloud-photos-to-google-drive/blob/main/pycloud/logger.py)

        A MagentoLogger instance will be attached to each Client object. Since the same Client object will be passed to all wrapper classes,
        each user will have all activity logged to their own file

        The package itself also has a MagentoLogger attached, which logs all activity across all Clients (future commit)

        :param name:        logger name - for a Client, the default name is "<username>_<domain>"
        :param log_file:    log file to save logs to - default is "<name>.log"
        :param level:       logging level for stdout logger; (files are set to DEBUG)
        """
        self.name = name
        self.logger = self.setup_logger(
            log_file=log_file,
            level=level
        )

    def setup_logger(self, log_file='', level=logging.DEBUG):
        """Configures and returns a logger. Uses existing loggers if possible"""
        logger = logging.getLogger(self.name)
        stdout_name = f'{self.name}_stdoutLogger'
        for handler in logger.handlers:
            if handler.name == stdout_name:
                return logger

        stdout_handler = logging.StreamHandler(stream=sys.stdout)
        stdout_handler.setFormatter(MagentoLogger.FORMATTER)
        stdout_handler.name = stdout_name

        if not log_file:
            log_file = f'{self.name}.log'

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(MagentoLogger.FORMATTER)

        logger.setLevel(level)
        logger.addHandler(stdout_handler)
        logger.addHandler(file_handler)
        return logger

    def format_msg(self, msg):
        return "|[{name}]|:  {message}".format(
            name=self.name,
            message=msg
        )

    def info(self, msg):
        return self.logger.info(
            self.format_msg(msg)
        )

    def debug(self, msg):
        return self.logger.debug(
            self.format_msg(msg)
        )

    def warning(self, msg):
        return self.logger.warning(
            self.format_msg(msg)
        )

    def error(self, msg):
        return self.logger.error(
            self.format_msg(msg)
        )

