"""
Fritz to Influx - import statistics from a FritzBox to InfluxDB for graphing.

Written by Paul Wayper

Licensed under the GPL v3.0.
"""

import argparse
from fritzconnection import FritzConnection
from fritzconnection.core.fritzconnection import FRITZ_IP_ADDRESS, FRITZ_TCP_PORT
from influxdb import InfluxDBClient
from os import environ
import time

# Connection to FritzBox
fritz_address = environ.get('FRITZBOX_ADDRESS', FRITZ_IP_ADDRESS)
fritz_password = environ.get('FRITZBOX_PASSWORD', 'admin')
fc = FritzConnection(address=fritz_address, password=fritz_password)

# Connection to InfluxDB
influx_address = environ.get('INFLUXDB_ADDRESS', 'localhost')
influx_username = environ.get('INFLUXDB_USERNAME', 'influxdb')
influx_password = environ.get('INFLUXDB_PASSWORD', 'influxdb')
db = InfluxDBClient(
    host=influx_address, username=influx_username,
    password=influx_password
)
db.switch_database('fritz.box')

# Get data from FritzBox
data_to_fetch = [
    {'section': 'WANCommonIFC', 'action': 'GetTotalBytesSent', 'properties': ['NewTotalBytesSent']},
    {'section': 'WANCommonIFC', 'action': 'GetTotalBytesReceived', 'properties': ['NewTotalBytesReceived']},
    {'section': 'WANIPConn', 'action': 'GetStatusInfo', 'properties': ['NewUptime']},
    {'section': 'WLANConfiguration1', 'action': 'GetStatistics', 'properties': ['NewTotalBytesSent', 'NewTotalPacketsReceived']},
    {'section': 'WLANConfiguration2', 'action': 'GetStatistics', 'properties': ['NewTotalBytesSent', 'NewTotalPacketsReceived']},
    {'section': 'WLANConfiguration3', 'action': 'GetStatistics', 'properties': ['NewTotalBytesSent', 'NewTotalPacketsReceived']},
]

def update_values(fc, db):
    """
    Get the data we're fetching from the FritzConnection and send it to the
    InfluxDB server
    """
    data_points = []
    for row in data_to_fetch:
        from_fritz = fc.call_action(row['section'], row['action'])
        # print(f"from fritz for {row['section']} {row['action']}: {from_fritz} should have properties {row['properties']}")
        data_points.append({
            'measurement': 'fritz.box',
            'tags': {
                'section': row['section'],
                'action': row['action'],
            },
            'fields': {
                property: from_fritz[property]
                for property in row['properties']
                if property in from_fritz
            }
        })
    
    # print("data_points:", data_points)
    result = db.write_points(data_points)
    print(f"At {time.time()} write_points returned {result}")

def fetch_on_schedule(fc, db, every=20):
    """
    Fetch points every 'every' seconds and send them to the database.
    """
    while True:
        start_time = time.time()
        update_values(fc, db)
        time.sleep(every - (time.time() - start_time) % every)

if __name__ == '__main__':
    fetch_on_schedule(fc, db, int(environ.get('FETCH_EVERY', '20')))

