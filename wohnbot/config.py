import logging
import yaml

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def get_default():
    return dict(
        logging=dict(
            level='INFO',
        ),
        scraping=dict(
            enabled = False,
            proxy = None,
            wgproxy_endpoint = None,
            sites = ['degewo', 'wbm', 'howoge', 'stadtundland', 'gewobag', 'gesobau', 'inberlinwohnen'],
            timeout = 10,
            parser = 'html.parser',
            write_sample = False,
            shelve_file = 'listings.data',
            max_pages = 20,
        ),
        telegram=dict(
            enabled = False,
            timeout = 10,
        ),
        influx=dict(
            enabled = False,
            host = 'localhost',
            port = 8086,
            database = 'wbmpoll',
            retention_period = '30d',
        ),
    )

def load(path="config.yml"):
    load_dotenv()
    try:
        with open(path) as stream:
            return yaml.safe_load(stream)
    except:
        logger.warning(f"Can't load {path}! Creating default config file.")
        config = get_default()
        save(config, path)
        return config

def save(config, path="config.yml"):
    logger.info(f"Writing config to {path}")
    with open(path, 'w') as stream:
        yaml.dump(config, stream)