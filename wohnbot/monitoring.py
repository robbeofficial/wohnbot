import logging

from influxdb import InfluxDBClient

def init(host, port, database):
    influx = InfluxDBClient(host, port)
    influx.create_database(database)
    influx.switch_database(database)
    logging.info(
        f"Writing metrics to influxb {host}:{port} {database}")
    return influx


def write(influx):
    pass