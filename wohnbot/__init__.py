import shelve

from wohnbot import config
params = config.load()

import logging
logging.basicConfig(level=params['logging']['level'])

from wohnbot.modules import dynamic_import

logger = logging.getLogger(__name__)
db = shelve.open(params['scraping']['shelve_file'])
mods = {site: dynamic_import(site) for site in params['scraping']['sites']}

