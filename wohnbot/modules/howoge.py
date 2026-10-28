import logging
from datetime import datetime
from urllib.parse import urljoin

import wohnbot
from wohnbot.exceptions import ScrapingError

logger = logging.getLogger(__name__)


def found(response):
    return (
        response.status_code == 200
        and not response.url.endswith('/404')
        and response.url != 'https://www.howoge.de/404-wohnungssuche.html'
    )


def scrape(session):
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-DE,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',        
        'Origin': 'https://www.howoge.de',
        'Pragma': 'no-cache',
        'Referer': 'https://www.howoge.de/immobiliensuche/wohnungssuche.html',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
    }

    data = {
        'tx_howrealestate_json_list[page]': '1',
        'tx_howrealestate_json_list[limit]': '12',
        'tx_howrealestate_json_list[lang]': '',
        'tx_howrealestate_json_list[rooms]': '',
    }

    response = session.post(
        'https://www.howoge.de/?type=999&tx_howrealestate_json_list[action]=immoList',
        headers=headers,
        data=data,
        timeout=wohnbot.params['scraping']['timeout'],
    )
    
    if 'crawler' in response.url:
        raise ScrapingError(f"Redirect to dummy data detected: {response.url}")

    return response.json()


def parse(scraped):
    base_url = 'https://www.howoge.de/'

    listings = scraped.get('immoobjects', [])
    logger.debug(f"Will parse {len(listings)} listings")

    seen_links = set()
    for listing in listings:
        link = urljoin(base_url, listing['link'])
        if link in seen_links:
            continue
        seen_links.add(link)

        yield {
            **listing,
            'link': link,
            'text': f"{listing['title']}, {listing['rooms']}-raum, {listing['area']}m², {listing['rent']}€, WBS:{listing['wbs']}",
            'found': str(datetime.now()),
        }
