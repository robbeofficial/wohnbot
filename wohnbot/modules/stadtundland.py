import logging
from datetime import datetime
from urllib.parse import urljoin, quote_plus

import requests
from bs4 import BeautifulSoup

import wohnbot
logger = logging.getLogger(__name__)


def found(response):
    return response.status_code == 200


def scrape():
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

    data = '{"offset":0,"cat":"wohnung"}'

    response = requests.post('https://d2396ha8oiavw0.cloudfront.net/sul-main/immoSearch', headers=headers, data=data)
    return response.json()


def parse(scraped):
    listings = scraped['data']
    logger.debug(f"Will parse {len(listings)} listings")
    
    base_url = 'https://stadtundland.de/wohnungssuche/'
    for listing in listings:

        yield {
            **listing,
            'link': urljoin(base_url, quote_plus(listing['details']['immoNumber'])),
            'text': listing['headline']
        }
    
