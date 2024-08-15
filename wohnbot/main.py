import logging
import time

import wohnbot
import wohnbot.sample
from wohnbot import influx

logger = logging.getLogger("wohnbot")

if __name__ == "__main__":
    for site in wohnbot.params['scraping']['sites']:
        module = wohnbot.mods[site]
        metrics = {}
        
        if wohnbot.params['scraping']['enabled']:
            scrape_start = time.time()
            scraped = module.scrape()
            scrape_end = time.time()
            metrics['request_duration'] = int((scrape_end - scrape_start) * 1000)
            if wohnbot.params['scraping']['write_sample']:
                wohnbot.sample.write(site, scraped)
        else:
            scraped = wohnbot.sample.load(site)
        
        processing_start = time.time()
        
        flats = list(module.parse(scraped))
        metrics['response_listings'] = len(flats)
        
        flats_new = []
        for item in flats:
            if not item['link'] in wohnbot.db:
                flats_new.append(item)
                wohnbot.db[item['link']] = item
        logger.info(f"Found {len(flats_new)} new flats on {site}")
        metrics["response_new_listings"] = len(flats_new)

        processing_end = time.time()
        metrics['processing_time'] = int((processing_end - processing_start) * 1000)
        
        if wohnbot.params['telegram']['enabled'] and len(flats_new) > 0:
            wohnbot.telegram.notify(flats_new, site, wohnbot.params['telegram']['timeout'])

        if wohnbot.params['influx']['enabled']:
            influx.write(site, metrics)