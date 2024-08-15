# wohnbot
Monitors Berlin municipal housing company websites for new rental listings

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