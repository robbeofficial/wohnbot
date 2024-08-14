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
```bash
source venv/bin/activate
python python -m wohnbot.wohnbot
```