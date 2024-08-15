from urllib.parse import urljoin
from datetime import datetime
import logging

import requests
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
    base_url = 'https://immosuche.degewo.de/'

    logger.info("Found {} flats".format(len(scraped['immos'])))

    for listing in scraped['immos']:
        yield {
            **listing,
            'link': urljoin(base_url, listing['property_path']),
            'text': f"{listing['headline']}",
            'found': str(datetime.now()),
        }


def scrape():
    headers = {
        'authority': 'immosuche.degewo.de',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-DE,en-US;q=0.9,en;q=0.8,de-DE;q=0.7,de;q=0.6,en-GB;q=0.5',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'referer': 'https://immosuche.degewo.de/de/search?size=10&page=1&property_type_id=1&categories%5B%5D=1&lat=&lon=&area=&address%5Bstreet%5D=&address%5Bcity%5D=&address%5Bzipcode%5D=&address%5Bdistrict%5D=&address%5Braw%5D=&district=&property_number=&price_switch=true&price_radio=null&price_from=&price_to=&qm_radio=null&qm_from=&qm_to=&rooms_radio=null&rooms_from=&rooms_to=&wbs_required=&order=rent_total_without_vat_asc',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    params = {
        'utf8': '✓',
        'property_type_id': '1',
        'categories[]': '1',
        'property_number': '',
        'address[raw]': '',
        'address[street]': '',
        'address[city]': '',
        'address[zipcode]': '',
        'address[district]': '',
        'district': '',
        'price_switch': 'false',
        'price_switch': 'on',
        'price_from': '',
        'price_to': '',
        'price_from': '',
        'price_to': '',
        'price_radio': 'null',
        'price_from': '',
        'price_to': '',
        'qm_radio': 'null',
        'qm_from': '',
        'qm_to': '',
        'rooms_radio': 'null',
        'rooms_from': '',
        'rooms_to': '',
        'features[]': '',
        'wbs_required': '',
        'order': 'rent_total_without_vat_asc',
    }

    immos = []
    unpaged = None

    for page in range(1, 20):
        params['page'] = str(page)

        response = requests.get('https://immosuche.degewo.de/de/search.json',
                                params=params, headers=headers, timeout=wohnbot.params['scraping']['timeout'])
        response_data = response.json()

        if not response_data.get('immos'):
            break

        if not unpaged:
            unpaged = response_data

        immos.extend(response_data['immos'])

    unpaged['immos'] = immos
    return unpaged
