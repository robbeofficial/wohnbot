import logging
import yaml

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def get_default():
    return dict(
        logging=dict(
            level='DEBUG'
        ),
        scraping=dict(
            enabled = False,
            #sites = ['degewo', 'wbm', 'howoge', 'stadtundland', 'gewobag', 'gesobau', 'inberlinwohnen'],
            sites = ['inberlinwohnen'],
            timeout = 10,
            parser = 'html.parser',
            write_sample = True,
            shelve_file = 'listings.data',
            max_pages = 20,
        ),
        telegram=dict(
            enabled=True,
            timeout=10,
        ),
        influx=dict(
            enabled=True,
            host='localhost',
            port=8086,
            database='wbmpoll',
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