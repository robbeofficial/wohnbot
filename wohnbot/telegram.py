import requests
import os
import logging

import wohnbot

logger = logging.getLogger(__name__)

def send_telegram_message(text):
    data = {
        "chat_id": os.getenv('TELEGRAM_CHAT_ID'),
        "text": text,
        "disable_notification": False,
        "disable_web_page_preview": True,
        "parse_mode": "HTML"
    }

    url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage"    
    send_message = requests.post(url, json=data, timeout=wohnbot.params['telegram']['timeout'])

    send_message.raise_for_status()

def build_telegram_message(flats_new, site):
    text = f'{len(flats_new)} new listings on {site}\n'
    for flat in flats_new:
        text += f'• <a href="{flat["link"]}">{flat["text"]}</a>\n'
    if len(text) > 4096:
        return f'{len(flats_new)} new listings on {site}'
    return text

def notify(flats_new, site):
    text = build_telegram_message(flats_new, site)
    logger.debug(f"Notify:\n{text}")
    if wohnbot.params['telegram']['enabled']:
        send_telegram_message(text)