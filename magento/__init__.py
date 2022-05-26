from . import clients
from . import search
from . import models
from . import entities
from . import utils

Client = clients.Client
logger = utils.MagentoLogger(
    name="magento",
    log_file='magento.log',
    stdout_level='WARNING'  # Clients will log to console
)
logger.debug('Initialized MyMagento')
