import json
import logging
from datetime import datetime
from urllib.parse import urljoin, quote_plus

import requests

import wohnbot

logger = logging.getLogger(__name__)


def found(response):
    if response.status_code != 200:
        return False
    if 'keine Details zu diesem Inserat anzeigen' in response.text:
        return False
    return True


def scrape(session):
    headers = {
        'accept': '*/*',
        'accept-language': 'en-DE,en-US;q=0.9,en;q=0.8,de-DE;q=0.7,de;q=0.6,en-GB;q=0.5,pl;q=0.4',
        'cache-control': 'no-cache',
        'content-type': 'text/plain;charset=UTF-8',
        'origin': 'https://stadtundland.de',
        'pragma': 'no-cache',
        'referer': 'https://stadtundland.de/',
        'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }

    all_data = []
    offset = 0
    limit = 100
    while True:
        data = json.dumps({'offset': offset, 'limit': limit, 'cat': 'wohnung'})

        # dont use session (VPN) here as site seems to occasionally block the IP
        response = requests.post(
            'https://d2396ha8oiavw0.cloudfront.net/sul-main/immoSearch',
            headers=headers,
            data=data,
            timeout=wohnbot.params['scraping']['timeout'],
        )
        res_json = response.json()
        batch = res_json.get('data', [])
        if not batch:
            break
        all_data.extend(batch)
        total_count = res_json.get('count', len(all_data))
        offset += len(batch)
        if offset >= total_count:
            break

    return {'data': all_data, 'count': len(all_data)}


def parse(scraped):
    listings = scraped.get('data', [])
    logger.debug(f"Will parse {len(listings)} listings")
    
    base_url = 'https://stadtundland.de/wohnungssuche/'
    seen_links = set()
    for listing in listings:
        immo_number = listing.get('details', {}).get('immoNumber')
        if not immo_number:
            continue
        link = urljoin(base_url, quote_plus(immo_number))
        if link in seen_links:
            continue
        seen_links.add(link)

        yield {
            **listing,
            'link': link,
            'text': listing.get('headline', ''),
            'found': str(datetime.now()),
        }
    
