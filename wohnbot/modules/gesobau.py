from datetime import datetime
from urllib.parse import urljoin
import logging

from bs4 import BeautifulSoup
import requests

import wohnbot

logger = logging.getLogger(__name__)


def found(response):
    return response.url != 'https://www.gesobau.de/mieten/wohnungssuche/angebot-nicht-mehr-verfuegbar.html'


def parse(unpaged):
    base_url = 'https://www.gesobau.de/'

    pages = unpaged.split('<!DOCTYPE html>')
    pages.pop(0)

    for page, text in enumerate(pages, 1):
        soup = BeautifulSoup(text, wohnbot.params['scraping']['parser'])
        items = soup.find_all('div', class_="results-entry")
        logger.debug(f"Found {len(items)} flats on page {page}")
        for item in items:
            props = {'found': str(datetime.now())}

            lines = [line.strip(', ') for line in item.text.splitlines() if line.strip()]

            yield {
                'link': urljoin(base_url, item.h3.a['href']),
                'text': ", ".join(lines),
                **props
            }

def scrape():
    cookies = {
        'CookieConsent': 'mandatory|video_google|marketing_facebook|statistics_matomo',
    }

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-DE,en-US;q=0.9,en;q=0.8,de-DE;q=0.7,de;q=0.6,en-GB;q=0.5,pl;q=0.4',
        'cache-control': 'no-cache',
        # 'cookie': 'CookieConsent=mandatory|video_google|marketing_facebook|statistics_matomo',
        'pragma': 'no-cache',
        'referer': 'https://www.gesobau.de/',
        'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }

    unpaged = ""

    for page in range(1,wohnbot.params['scraping']['max_pages']):
        params = {
            'tx_solr[page]': page,
        }

        response = requests.get('https://www.gesobau.de/mieten/wohnungssuche/', params=params, cookies=cookies, headers=headers)

        unpaged += response.text

        if '>&raquo;</a>' not in response.text:
            break

    return unpaged

