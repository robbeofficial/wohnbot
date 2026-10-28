import logging
from datetime import datetime

from bs4 import BeautifulSoup

import wohnbot

logger = logging.getLogger(__name__)


def found(response):
    return response.status_code == 200 and response.url != 'https://www.gewobag.de/mietangebot-nicht-gefunden/'


def scrape(session):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
        # 'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Referer': 'https://www.gewobag.de/fuer-mietinteressentinnen/mietangebote/',
        'DNT': '1',
        'Connection': 'keep-alive',
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

    unpaged = ""
    for page in range(1, wohnbot.params['scraping']['max_pages']):
        url = (
            f'https://www.gewobag.de/fuer-mietinteressentinnen/mietangebote/page/{page}/'
            if page > 1
            else 'https://www.gewobag.de/fuer-mietinteressentinnen/mietangebote/'
        )
        response = session.get(
            url,
            params=params,
            headers=headers,
            timeout=wohnbot.params['scraping']['timeout']
        )
        if response.status_code != 200 or 'angebot-content' not in response.text:
            break

        unpaged += response.text

        if 'next page-numbers' not in response.text:
            break

    return unpaged


def parse(html_input):
    soup = BeautifulSoup(html_input, wohnbot.params['scraping']['parser'])

    items = soup.find_all('div', class_='angebot-content')
    logger.debug(f"Will parse {len(items)} flats")

    seen_links = set()
    for item in items:
        props = {'found': str(datetime.now())}

        title_el = item.find('h3', class_='angebot-title')
        title = title_el.text.strip() if title_el else ''
        addr_el = item.find('address')
        address = addr_el.text.strip() if addr_el else ''
        link_el = item.find('a', href=True, class_='read-more-link')
        if not link_el:
            continue
        url = link_el['href']

        if url in seen_links:
            continue
        seen_links.add(url)

        table = item.find('table', class_='angebot-info')
        if table:
            for tr in table.find_all('tr'):
                if tr.th and tr.td:
                    key = tr.th.text.strip()
                    value = tr.td.text.strip()
                    props[key] = value

        yield {
            **props,
            "link": url,
            "text": f"{title} | {address}",
        }
