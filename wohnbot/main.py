import logging

import wohnbot
import wohnbot.sample

logger = logging.getLogger("wohnbot")

if __name__ == "__main__":
    for site in wohnbot.params['scraping']['sites']:
        module = wohnbot.mods[site]
        if wohnbot.params['scraping']['enabled']:
            scraped = module.scrape()
            if wohnbot.params['scraping']['write_sample']:
                wohnbot.sample.write(site, scraped)
        else:
            scraped = wohnbot.sample.load(site)
        flats = list(module.parse(scraped))
        flats_new = []
        for item in flats:
            if not item['link'] in wohnbot.db:
                flats_new.append(item)
                wohnbot.db[item['link']] = item
        logger.info(f"Found {len(flats_new)} new flats on {site}")

        if wohnbot.params['telegram']['enabled'] and len(flats_new) > 0:
            wohnbot.telegram.notify(flats_new, site, wohnbot.params['telegram']['timeout'])