from . import clients
from . import search
from . import models
from . import entities
from . import utils

import logging
logger = utils.MagentoLogger(name='MyMagento', log_file='magento.log', level=logging.DEBUG)

Client = clients.Client


