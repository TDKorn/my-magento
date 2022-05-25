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


LOG_FORMATTER = logging.Formatter(
    fmt="%(asctime)s %(levelname)-2s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def setup_logger(name, log_file='', level=logging.INFO):
    """Configures and returns a logger. Uses existing loggers if possible"""
    logger = logging.getLogger(name)
    stdout_name = f'{name}_stdoutLogger'
    for handler in logger.handlers:
        if handler.name == stdout_name:
            return logger

    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setFormatter(LOG_FORMATTER)
    stdout_handler.name = stdout_name

    if not log_file:
        log_file = f'{name}.log'

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(LOG_FORMATTER)

    logger.setLevel(level)
    logger.addHandler(stdout_handler)
    logger.addHandler(file_handler)
    return logger
