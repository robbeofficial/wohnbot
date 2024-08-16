import logging
import time
import traceback

import wohnbot
import wohnbot.sample
from wohnbot import influx

logger = logging.getLogger("wohnbot")

def log_exception(e, site):
    exc_type = e.__class__.__name__
    exc_message = str(e)
    exc_strack_trace = ''.join(traceback.format_tb(e.__traceback__))
    exc_full = ''.join(traceback.format_exception(e))

    tags = {
        "type": exc_type,
        "site": site,
    }

    fields = {
        "message": exc_message,
        "stack_trace": exc_strack_trace,
        "count": 1,
    }
    
    influx.add("exceptions",fields, tags)
    logger.error(f"Exception handling site {site}:\n" + exc_full)
    

def process_site(site):
    module = wohnbot.mods[site]

    if wohnbot.params['scraping']['enabled']:
        scrape_start = time.time()
        scraped = module.scrape()
        scrape_duration_ms = int((time.time() - scrape_start) * 1000)
        influx.add('metrics', {'request_duration': scrape_duration_ms}, {'site': site})
        
        if wohnbot.params['scraping']['write_sample']:
            wohnbot.sample.write(site, scraped)
    else:
        scraped = wohnbot.sample.load(site)
    
    processing_start = time.time()
    
    flats = list(module.parse(scraped))
    influx.add('metrics', {'response_listings': len(flats)}, {'site': site})
    
    flats_new = []
    for item in flats:
        if not item['link'] in wohnbot.db:
            flats_new.append(item)
            wohnbot.db[item['link']] = item
    logger.info(f"Found {len(flats_new)} new flats on {site}")
    influx.add('metrics', {'response_new_listings': len(flats_new)}, {'site': site})

    processing_duration_ms = int((time.time() - processing_start) * 1000)
    influx.add('metrics', {'processing_time': processing_duration_ms}, {'site': site})

    if wohnbot.params['telegram']['enabled'] and len(flats_new) > 0:
        wohnbot.telegram.notify(flats_new, site, wohnbot.params['telegram']['timeout'])

if __name__ == "__main__":
    for site in wohnbot.params['scraping']['sites']:
        try:
            process_site(site)
        except Exception as e:
            log_exception(e, site)
    influx.flush()