# wohnbot
Monitors Berlin municipal housing company websites for new rental listings. Supports fast IP address switching using https://github.com/robbeofficial/wgproxy.

# Setup
```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

# Configuration
- set credentials for telegram notifications in `.env` file: 
```
TELEGRAM_CHAT_ID=...
TELEGRAM_BOT_TOKEN=...
```
- optional: also publish every new listing to an Upstash Redis stream. Add the REST credentials to `.env` and set `redis.enabled: true` in `config.yml`:
```
UPSTASH_REDIS_REST_URL=...
UPSTASH_REDIS_REST_TOKEN=...
```
Each listing becomes one entry in the stream `redis.key` (default `wohnbot:listings`, trimmed to about `redis.maxlen` entries) with the fields `site`, `link`, `text`, `seen_at` and `data` (the full listing as JSON). Read them with `XRANGE` / `XREAD`. A Redis failure is retried and logged but never blocks the Telegram message.
- adjust `config.yml` to your needs

# Usage
Check for new listings
```bash
python -m wohnbot.main
```

Dump cached listings from shelve file to JSON
```bash
python -m wohnbot.dump > dump.json
```

# TODOs
- add rate limiter
