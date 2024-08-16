import logging

from influxdb import InfluxDBClient

import wohnbot

logger = logging.getLogger(__name__)

def parse_duration(duration_str):
    unit_to_seconds = {
        'u': 1e-6, 'ms': 1e-3, 's': 1, 'm': 60, 'h': 3600, 'd': 86400, 'w': 604800, 'y': 31536000
    }

    duration_str = duration_str.strip().lower()
    total_seconds = 0
    temp = ''
    
    for char in duration_str:
        if char.isdigit():
            temp += char
        else:
            if temp:
                total_seconds += int(temp) * unit_to_seconds.get(char, 1)
                temp = ''
            elif char in unit_to_seconds:
                total_seconds += unit_to_seconds[char]

    return total_seconds

def connect():
    host = wohnbot.params['influx']['host']
    port = wohnbot.params['influx']['port']
    database = wohnbot.params['influx']['database']
    duration = wohnbot.params['influx']['retention_period']
    policy_name = 'wohnbot'

    logger.info(f"Writing metrics to influxb '{database}' at '{host}:{port}'")
    client = InfluxDBClient(host, port)
    client.create_database(database)
    client.switch_database(database)

    retention_policies = client.get_list_retention_policies(database)
    existing_policy = next((policy for policy in retention_policies if policy['name'] == policy_name), None)
    if existing_policy:
        if parse_duration(existing_policy['duration']) != parse_duration(duration):
            logger.info(f"Altering retention period to '{duration}'")
            client.alter_retention_policy(policy_name, database, duration, '1', True, duration)
    else:
        logger.info(f"Creating retention policy with period of '{duration}'")
        client.create_retention_policy('wohnbot', duration, '1', database, True, duration)
    
    return client

def add(measurement, fields, tags):
    if wohnbot.params['influx']['enabled']:
        points.append({'measurement': measurement, 'fields': fields, 'tags': tags})

def flush():
    if wohnbot.params['influx']['enabled']:
        logger.debug(f"Writing {len(points)} points")
        client.write_points(points)
        points.clear()

if wohnbot.params['influx']['enabled']:
    client = connect()
    points = []