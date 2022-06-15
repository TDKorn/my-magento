from . import clients
from . import search
from . import models
from . import entities
from . import utils

Client = clients.Client
logger = utils.MagentoLogger(
    name=utils.MagentoLogger.PACKAGE_LOG_NAME,
    log_file=utils.MagentoLogger.PACKAGE_LOG_NAME + '.log',
    stdout_level='WARNING'  # Clients will log to console
)
logger.debug('Initialized MyMagento')
