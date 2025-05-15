import logging
from datetime import datetime

from bs4 import BeautifulSoup

import wohnbot

logger = logging.getLogger(__name__)


def found(response):
    return response.url != 'https://www.gewobag.de/mietangebot-nicht-gefunden/'


def scrape(session):
    import requests

    cookies = {
        'borlabs-cookie': '%7B%22consents%22%3A%7B%22essential%22%3A%5B%22borlabs-cookie%22%2C%22accessibility_contrast%22%2C%22accessibility_test_size%22%2C%22location_agreement%22%5D%7D%2C%22domainPath%22%3A%22www.gewobag.de%2F%22%2C%22expires%22%3A%22Mon%2C%2018%20Aug%202025%2015%3A02%3A31%20GMT%22%2C%22uid%22%3A%22anonymous%22%2C%22v3%22%3Atrue%2C%22version%22%3A2%7D',
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
        # 'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Referer': 'https://www.gewobag.de/fuer-mietinteressentinnen/mietangebote/',
        'DNT': '1',
        'Connection': 'keep-alive',
        # 'Cookie': 'borlabs-cookie=%7B%22consents%22%3A%7B%22essential%22%3A%5B%22borlabs-cookie%22%2C%22accessibility_contrast%22%2C%22accessibility_test_size%22%2C%22location_agreement%22%5D%7D%2C%22domainPath%22%3A%22www.gewobag.de%2F%22%2C%22expires%22%3A%22Mon%2C%2018%20Aug%202025%2015%3A02%3A31%20GMT%22%2C%22uid%22%3A%22anonymous%22%2C%22v3%22%3Atrue%2C%22version%22%3A2%7D',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Priority': 'u=0, i',
    }

    params = {
        'objekttyp[]': 'wohnung',
        'gesamtmiete_von': '',
        'gesamtmiete_bis': '',
        'gesamtflaeche_von': '',
        'gesamtflaeche_bis': '',
        'zimmer_von': '',
        'zimmer_bis': '',
        'sort-by': '',
    }

    response = requests.get(
        'https://www.gewobag.de/fuer-mietinteressentinnen/mietangebote/',
        params=params,
        # cookies=cookies,
        headers=headers,
    )
    return response.text


def parse(html_input):
    soup = BeautifulSoup(html_input, wohnbot.params['scraping']['parser'])

    if soup.find('div', class_='empty-mietangebote'):
        return []

    item_container = soup.find('div', class_='filtered-mietangebote')
    items = item_container.find_all('div', class_='angebot-content')
    logger.debug(f"Will parse {len(items)} flats")
    for item in items:
        props = {'found': str(datetime.now())}

        title = item.find('h3', class_='angebot-title').text
        address = item.find('address').text.strip()
        url = item.find('a', href=True, class_='read-more-link')['href']

        for tr in item.find('table', class_='angebot-info').find_all('tr'):
            key = tr.th.text
            value = tr.td.text
            props[key] = value

        # tags = []
        # for li in item.find('ul', class_='angebot-characteristics').find_all('li'):
        #   tags.append(li.text)
        # props["tags"] = tags

        yield {
            **props,
            "link": url,
            "text": f"{title} | {address}",
        }
