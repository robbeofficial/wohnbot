import logging
import shelve
import json
import time
import glob
import importlib
import requests
import os

import wohnbot.config

logger = logging.getLogger(__name__)

def write_sample(site, scraped):
    json_output = type(scraped) is dict
    fname = f"samples/{site}-{round(time.time() * 1000)}.{'json' if json_output else 'html'}"
    logger.warning(f"Writing sample file for {site} to {fname}")
    with open(fname, "w") as f:
        if json_output:
            json.dump(scraped, f)
        else:
            f.write(scraped)

def load_sample(site):
    logger.warning("Loading latest sample file for {}".format(site))
    try:
        with open(glob.glob(f"samples/{site}-*.html")[-1], "r") as f:
            return f.read()
    except:
        with open(glob.glob(f"samples/{site}-*.json")[-1], "r") as f:
            return json.load(f)

def import_site_modules(sites):
    modules = {}
    for site in sites:
        module_name = f"wohnbot.modules.{site}"
        logger.info(f"Importing {module_name}")
        modules[site] = importlib.import_module(module_name)
    return modules

def send_telegram_message(text, timeout):
    data = {
        "chat_id": os.getenv('TELEGRAM_CHAT_ID'),
        "text": text,
        "disable_notification": False,
        "disable_web_page_preview": True,
        "parse_mode": "HTML"
    }

    url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage"    
    send_message = requests.post(url, json=data, timeout=timeout)

    send_message.raise_for_status()

def build_telegram_message(flats_new, site):
    text = f'{len(flats_new)} new listings on {site}\n'
    for flat in flats_new:
        text += f'• <a href="{flat["link"]}">{flat["text"]}</a>\n'
    if len(text) <= 4096:
        text = f'{len(flats_new)} new listings on {site}'
    return text

config = wohnbot.config.load()
logging.basicConfig(level=config['logging']['level'])

db = shelve.open(config['scraping']['shelve_file'])

modules = import_site_modules(config['scraping']['sites'])

for site in config['scraping']['sites']:
    module = modules[site]
    if config['scraping']['enabled']:
        scraped = module.scrape(config['scraping']['timeout'])
        if config['scraping']['write_sample']:
            write_sample(site, scraped)
    else:
        scraped = load_sample(site)
    flats = list(module.parse(scraped))
    flats_new = []
    for item in flats:
        if not item['link'] in db:
            flats_new.append(item)
            db[item['link']] = item
    logger.info(f"Found {len(flats_new)} new flats on {site}")

    if config['telegram']['enabled'] and len(flats_new) > 0:
        text = build_telegram_message(flats_new, site)
        send_telegram_message(text, config['telegram']['timeout'])
    

    

