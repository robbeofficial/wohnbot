import logging

from influxdb import InfluxDBClient

import wohnbot

def connect(host, port, database):
    influx = InfluxDBClient(host, port)
    influx.create_database(database)
    influx.switch_database(database)
    logging.debug(f"Writing metrics to influxb {host}:{port} {database}")
    return influx

def write(name, fields = {}, tags = {}):
    if wohnbot.params['influx']['enabled']:
        measurement = [{"measurement": name, "fields": fields, "tags": tags}]
        client.write_points(measurement)

if wohnbot.params['influx']['enabled']:
    client = connect(wohnbot.params['influx']['host'], wohnbot.params['influx']['port'], wohnbot.params['influx']['database'])