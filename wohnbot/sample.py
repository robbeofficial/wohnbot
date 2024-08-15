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

def latest_sample_path(site, ext):
    files = glob.glob(f"samples/{site}-*.{ext}")
    if files:
        return sorted(files)[-1]
    
def load_html(path):
    logger.info(f"Loading sample from {path}")
    return open(path, "r").read()

def load_json(path):
    logger.info(f"Loading sample from {path}")
    return json.load(open(path, "r"))

def load(site):    
    path = latest_sample_path(site, 'html')
    if path:
        return load_html(path)
    
    path = latest_sample_path(site, 'json')
    if path:
        return load_json(path)
    
    logger.error("No HTML or JSON sample found! Set scraping.enabled and scraping.write_sample in config.yml to true to record a new sample.")
    exit(1)