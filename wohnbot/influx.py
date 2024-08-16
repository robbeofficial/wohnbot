import logging

from influxdb import InfluxDBClient

import wohnbot

logger = logging.getLogger(__name__)

def connect(host, port, database):
    influx = InfluxDBClient(host, port)
    influx.create_database(database)
    influx.switch_database(database)
    logger.debug(f"Writing metrics to influxb {host}:{port} {database}")
    return influx

def add(measurement, fields, tags):
    if wohnbot.params['influx']['enabled']:
        points.append({'measurement': measurement, 'fields': fields, 'tags': tags})

def flush():
    if wohnbot.params['influx']['enabled']:
        logger.debug(f"Writing {len(points)} points")
        client.write_points(points)
        points.clear()

if wohnbot.params['influx']['enabled']:
    client = connect(wohnbot.params['influx']['host'], wohnbot.params['influx']['port'], wohnbot.params['influx']['database'])
    points = []