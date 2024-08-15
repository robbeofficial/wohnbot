import logging
import re
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def found(response):
    return response.url != 'https://www.wbm.de/wohnungen-berlin/angebote/nicht-mehr-verfuegbar/'


def scrape(timeout=None):
    req = requests.get('https://www.wbm.de/wohnungen-berlin/angebote/', timeout=timeout)
    return req.text


def parse(html_input, parser='html.parser'):
    soup = BeautifulSoup(html_input, parser)

    base_url = 'https://www.wbm.de/'

    items = soup.find_all('div', class_='openimmo-search-list-item')

    logger.info("Will parse {} flats".format(len(items)))

    for item in items:

        first_p = item.find('p')
        text = re.sub('\s+', ' ', first_p.text).strip()

        link = item.find('a', href=True)
        url = urljoin(base_url, link['href'])

        props = {'found': str(datetime.now())}

        main_properties = item.find_all('li', class_='main-property')
        for main_property in main_properties:
            divs = main_property.find_all('div')
            key = divs[0].text.strip(' :')
            value = divs[1].text.strip()
            props[key] = value

        yield {
            'link': url,
            'text': text,
            **props
        }
