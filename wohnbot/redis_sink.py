"""Publish every new listing to an Upstash Redis stream (REST API).

Each listing becomes one stream entry (XADD) with the fields:
    site, link, text, seen_at (UTC ISO 8601), data (the full listing as JSON)

A consumer can read them with XRANGE / XREAD and keep its own last-seen id.
Credentials come from the environment (.env):
    UPSTASH_REDIS_REST_URL, UPSTASH_REDIS_REST_TOKEN
"""
import json
import logging
import os
import time
from datetime import datetime, timezone

import requests

import wohnbot

logger = logging.getLogger(__name__)

DEFAULT_KEY = 'wohnbot:listings'
DEFAULT_MAXLEN = 1000
DEFAULT_TIMEOUT = 10
ATTEMPTS = 3


def get_credentials():
    url = os.getenv('UPSTASH_REDIS_REST_URL')
    token = os.getenv('UPSTASH_REDIS_REST_TOKEN')
    if not url or not token:
        return None, None
    return url.rstrip('/'), token


def build_commands(flats_new, site, key=DEFAULT_KEY, maxlen=DEFAULT_MAXLEN, now=None):
    """One XADD per listing. Stream is trimmed to roughly `maxlen` entries."""
    seen_at = (now or datetime.now(timezone.utc)).isoformat()
    commands = []
    for flat in flats_new:
        commands.append([
            'XADD', key, 'MAXLEN', '~', str(maxlen), '*',
            'site', site,
            'link', str(flat.get('link', '')),
            'text', str(flat.get('text', '')),
            'seen_at', seen_at,
            'data', json.dumps(flat, ensure_ascii=False, default=str),
        ])
    return commands


def send_pipeline(commands, url, token, timeout=DEFAULT_TIMEOUT):
    """POST all commands in one request; raise if any of them failed."""
    response = requests.post(
        f'{url}/pipeline',
        headers={'Authorization': f'Bearer {token}'},
        json=commands,
        timeout=timeout,
    )
    response.raise_for_status()
    errors = [item['error'] for item in response.json() if isinstance(item, dict) and 'error' in item]
    if errors:
        raise RuntimeError(f'Upstash rejected {len(errors)} of {len(commands)} commands: {errors[0]}')


def publish(flats_new, site):
    """Never raises: a Redis problem must not stop the Telegram notification."""
    config = wohnbot.params.get('redis') or {}
    if not config.get('enabled') or not flats_new:
        return

    url, token = get_credentials()
    if not url:
        logger.warning('redis enabled but UPSTASH_REDIS_REST_URL / UPSTASH_REDIS_REST_TOKEN are not set')
        return

    commands = build_commands(
        flats_new, site,
        key=config.get('key', DEFAULT_KEY),
        maxlen=config.get('maxlen', DEFAULT_MAXLEN),
    )
    timeout = config.get('timeout', DEFAULT_TIMEOUT)

    for attempt in range(1, ATTEMPTS + 1):
        try:
            send_pipeline(commands, url, token, timeout)
            logger.info(f'Published {len(commands)} listing(s) from {site} to redis')
            return
        except Exception as e:
            logger.warning(f'Redis publish attempt {attempt}/{ATTEMPTS} failed: {type(e).__name__}: {e}')
            if attempt < ATTEMPTS:
                time.sleep(attempt)
    logger.error(f'Giving up publishing {len(commands)} listing(s) from {site} to redis')
