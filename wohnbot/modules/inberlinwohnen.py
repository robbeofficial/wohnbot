from datetime import datetime
from urllib.parse import urljoin
import logging

from bs4 import BeautifulSoup
from wohnbot.exceptions import ScrapingError

import wohnbot

logger = logging.getLogger(__name__)

def found(response):
    return response.status_code == 200


def scrape(session):
    response = session.get('https://inberlinwohnen.de/wohnungsfinder/', timeout=wohnbot.params['scraping']['timeout'])
    if response.status_code != 200:
        raise ScrapingError(f"Failed to scrape inberlinwohnen.de, got status code {response.status_code}")
    
    return response.text


def parse(html_input):
    soup = BeautifulSoup(html_input, wohnbot.params['scraping']['parser'])
    base_url = 'https://inberlinwohnen.de/'

    items = soup.find_all('li', class_='tb-merkflat')

    logger.debug("Will parse {} flats".format(len(items)))

    for item in items:

        props = {'found': str(datetime.now())}
        trs = item.find_all('tr')
        for tr in trs:
            key = tr.th.text.strip(' :')
            value = tr.td.text.strip()
            props[key] = value

        title = item.h3.text.strip()
        link = item.find('a', class_='org-but')
        url = urljoin(base_url, link['href'])

        yield {
            'link': url,
            'text': title,
            **props
        }
