import wohnbot
import json

if __name__ == "__main__":
    print(json.dumps(list(wohnbot.db.values()),indent=1))