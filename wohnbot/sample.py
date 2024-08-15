import time
import glob
import logging
import json

logger = logging.getLogger(__name__)

def write(site, scraped):
    json_output = type(scraped) is dict
    fname = f"samples/{site}-{round(time.time() * 1000)}.{'json' if json_output else 'html'}"
    logger.warning(f"Writing sample file for {site} to {fname}")
    with open(fname, "w") as f:
        if json_output:
            json.dump(scraped, f)
        else:
            f.write(scraped)

def load_html(site):
    try:
        with open(glob.glob(f"samples/{site}-*.html")[-1], "r") as f:
            return f.read()
    except:
        return None

def load_json(site):
    try:
        with open(glob.glob(f"samples/{site}-*.json")[-1], "r") as f:
            return json.load(f)
    except:
        return None

def load(site):
    logger.info("Loading latest sample file for {}".format(site))
    sample = load_html(site)
    if not sample:
        sample = load_json(site)
    if not sample:
        logger.error("No HTML or JSON sample found! Set scraping.enabled and scraping.write_sample in config.yml to true to record a new sample.")
        exit(1)
    return sample