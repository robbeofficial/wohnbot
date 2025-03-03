from urllib.parse import urljoin
from datetime import datetime
import logging

from bs4 import BeautifulSoup

import wohnbot

logger = logging.getLogger(__name__)

def found(response):
    # <h1 class="article__title--alert">Objekt nicht mehr verfügbar</h1>
    soup = BeautifulSoup(response.text, wohnbot.params['scraping']['parser'])
    alert = soup.find('h1', class_="article__title--alert")
    if alert and alert.text.strip() == "Objekt nicht mehr verfügbar":
        return False
    return True


def parse(scraped):
    soup = BeautifulSoup(scraped, wohnbot.params['scraping']['parser'])
    base_url = 'https://www.degewo.de/immosuche'

    items = soup.find_all('article', class_="article-list__item--immosearch")

    logger.debug("Found {} flats".format(len(items)))

    for item in items:
        props = {'found': str(datetime.now())}
        lines = [line.strip(', ') for line in item.text.splitlines() if line.strip()]

        yield {
            'link': urljoin(base_url, item.a['href']),
            'text': ", ".join(lines),
            **props
        }


def scrape(session):
    import requests

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://www.degewo.de/',
        'Origin': 'https://www.degewo.de',
        'Connection': 'keep-alive',
        # 'Cookie': 'cookie-marketing=accept; cookie-services=accept; cookie-maps=accept; cookie-immo=accept; cookie-youtube=accept; cookie-webcam=accept; degewo-cookie-consent=true; fe_typo_user=813130d9b7354d8b48eaea0720481694.b22bf4f763d065349de1828a1bc0da28b8e4b3faf6bc13ea28f13b89d79086c4; TS01eb0cb4=019c25b6b423e3d2b09af77286c82970d084e873c35b16e5964f79f3b3cb554e8c4ea2fff753c5d1f2d807037227511766efa909bb',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Priority': 'u=0, i',
        # Requests doesn't support trailers
        # 'TE': 'trailers',
    }

    params = {
        'tx_openimmo_immobilie[search]': 'paginate',
        'tx_openimmo_immobilie[page]': '1',
        'tx_openimmo_immobilie[latitude]': '',
        'tx_openimmo_immobilie[longitude]': '',
        'tx_openimmo_immobilie[location]': '',
        'tx_openimmo_immobilie[nettokaltmiete]': '',
        'tx_openimmo_immobilie[nettokaltmiete_start]': '',
        'tx_openimmo_immobilie[nettokaltmiete_end]': '',
        'tx_openimmo_immobilie[warmmiete]': '',
        'tx_openimmo_immobilie[warmmiete_start]': '',
        'tx_openimmo_immobilie[warmmiete_end]': '',
        'tx_openimmo_immobilie[wohnflaeche]': '',
        'tx_openimmo_immobilie[wohnflaeche_start]': '',
        'tx_openimmo_immobilie[wohnflaeche_end]': '',
        'tx_openimmo_immobilie[anzahlZimmer]': '',
        'tx_openimmo_immobilie[anzahlZimmer_start]': '',
        'tx_openimmo_immobilie[anzahlZimmer_end]': '',
        'tx_openimmo_immobilie[ausstattung][]': '',
        'tx_openimmo_immobilie[ausstattung]': '',
        'tx_openimmo_immobilie[wbsSozialwohnung]': '',
        'tx_openimmo_immobilie[sortBy]': 'immobilie_preise_nettokaltmiete',
        'tx_openimmo_immobilie[sortOrder]': 'asc',
        'tx_openimmo_immobilie[regionalerZusatz]': '',
    }

    unpaged = ""

    for page in range(1,wohnbot.params['scraping']['max_pages']):
        params['tx_openimmo_immobilie[page]'] = str(page)

        response = session.post('https://www.degewo.de/immosuche#openimmo-search-result', headers=headers, data=params, timeout=wohnbot.params['scraping']['timeout'])
        
        with open(f'response{page}.html','w') as f:
            f.write(response.text)

        unpaged += response.text

        if 'article-list__item--immosearch' not in response.text:
            break

    return unpaged
