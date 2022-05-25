from . import clients
from . import search
from . import models
from . import entities
from . import utils

import logging
logging.basicConfig(filename=f'magento.log', level=logging.DEBUG)
LOGGER = utils.setup_logger('MyMagento', log_file='magento.log')


Client = clients.Client

