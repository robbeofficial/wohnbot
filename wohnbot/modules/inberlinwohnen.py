from datetime import datetime
from urllib.parse import urljoin
import logging

import requests
from bs4 import BeautifulSoup

import wohnbot

logger = logging.getLogger(__name__)

def found(response):
    return response.status_code == 200


def scrape():
    req = requests.get('https://inberlinwohnen.de/wohnungsfinder/', timeout=wohnbot.params['scraping']['timeout'])
    return req.text


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
