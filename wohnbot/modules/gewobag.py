import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup

import wohnbot

logger = logging.getLogger(__name__)


def found(response):
    return response.url != 'https://www.gewobag.de/mietangebot-nicht-gefunden/'


def scrape():
    cookies = {
        'borlabs-cookie': '%7B%22consents%22%3A%7B%22essential%22%3A%5B%22borlabs-cookie%22%2C%22accessibility_contrast%22%2C%22accessibility_test_size%22%2C%22language_switch%22%2C%22location_agreement%22%5D%2C%22statistics%22%3A%5B%22matomo%22%5D%2C%22external-media%22%3A%5B%22gewobag-youtube%22%2C%22googlemaps%22%5D%7D%2C%22domainPath%22%3A%22www.gewobag.de%2F%22%2C%22expires%22%3A%22Fri%2C%2006%20Oct%202023%2017%3A56%3A09%20GMT%22%2C%22uid%22%3A%22g502zxlo-73pjh7xi-zuj2rk6a-ewv9i5af%22%2C%22version%22%3A%223%22%7D',
    }

    headers = {
        'authority': 'www.gewobag.de',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-DE,en-US;q=0.9,en;q=0.8,de-DE;q=0.7,de;q=0.6,en-GB;q=0.5',
        'cache-control': 'no-cache',
        # 'cookie': 'borlabs-cookie=%7B%22consents%22%3A%7B%22essential%22%3A%5B%22borlabs-cookie%22%2C%22accessibility_contrast%22%2C%22accessibility_test_size%22%2C%22language_switch%22%2C%22location_agreement%22%5D%2C%22statistics%22%3A%5B%22matomo%22%5D%2C%22external-media%22%3A%5B%22gewobag-youtube%22%2C%22googlemaps%22%5D%7D%2C%22domainPath%22%3A%22www.gewobag.de%2F%22%2C%22expires%22%3A%22Fri%2C%2006%20Oct%202023%2017%3A56%3A09%20GMT%22%2C%22uid%22%3A%22g502zxlo-73pjh7xi-zuj2rk6a-ewv9i5af%22%2C%22version%22%3A%223%22%7D',
        'pragma': 'no-cache',
        'referer': 'https://www.gewobag.de/fuer-mieter-und-mietinteressenten/mietangebote/',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    }

    params = {
        'bezirke_all': '1',
        'bezirke[]': [
            'charlottenburg-wilmersdorf',
            'charlottenburg-wilmersdorf-charlottenburg',
            'friedrichshain-kreuzberg',
            'friedrichshain-kreuzberg-friedrichshain',
            'friedrichshain-kreuzberg-kreuzberg',
            'lichtenberg',
            'lichtenberg-alt-hohenschoenhausen',
            'lichtenberg-falkenberg',
            'lichtenberg-fennpfuhl',
            'marzahn-hellersdorf',
            'marzahn-hellersdorf-marzahn',
            'mitte',
            'mitte-gesundbrunnen',
            'mitte-moabit',
            'mitte-wedding',
            'neukoelln',
            'neukoelln-britz',
            'neukoelln-buckow',
            'neukoelln-rudow',
            'pankow',
            'pankow-prenzlauer-berg',
            'reinickendorf',
            'reinickendorf-hermsdorf',
            'reinickendorf-tegel',
            'reinickendorf-waidmannslust',
            'spandau',
            'spandau-hakenfelde',
            'spandau-haselhorst',
            'spandau-staaken',
            'spandau-wilhelmstadt',
            'steglitz-zehlendorf',
            'steglitz-zehlendorf-lichterfelde',
            'steglitz-zehlendorf-steglitz',
            'tempelhof-schoeneberg',
            'tempelhof-schoeneberg-lichtenrade',
            'tempelhof-schoeneberg-mariendorf',
            'tempelhof-schoeneberg-marienfelde',
            'tempelhof-schoeneberg-schoeneberg',
            'treptow-koepenick',
            'treptow-koepenick-altglienicke',
            'treptow-koepenick-niederschoeneweide',
        ],
        'nutzungsarten[]': 'wohnung',
        'gesamtmiete_von': '',
        'gesamtmiete_bis': '',
        'gesamtflaeche_von': '',
        'gesamtflaeche_bis': '',
        'zimmer_von': '',
        'zimmer_bis': '',
        'sort-by': 'recent',
    }

    response = requests.get('https://www.gewobag.de/fuer-mieter-und-mietinteressenten/mietangebote/',
                            params=params, cookies=cookies, headers=headers, timeout=wohnbot.params['scraping']['timeout'])
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
