"""
Fritz to Influx - import statistics from a FritzBox to InfluxDB for graphing.

Written by Paul Wayper

Licensed under the GPL v3.0.
"""

import argparse
from fritzconnection import FritzConnection
from fritzconnection.core.fritzconnection import FRITZ_IP_ADDRESS, FRITZ_TCP_PORT
from fritzconnection.core.exceptions import FritzActionError
from influxdb import InfluxDBClient
from os import environ
import time

# Connection to FritzBox
fritz_address = environ.get('FRITZBOX_ADDRESS', FRITZ_IP_ADDRESS)
fritz_username = environ.get('FRITZBOX_USERNAME')
fritz_password = environ.get('FRITZBOX_PASSWORD')
if not fritz_password:
    print("Warning: environment FRITZBOX_PASSWORD not set - using default")
    fritz_password = 'admin'
fc = FritzConnection(
    address=fritz_address, password=fritz_password,
    # user=fritz_username, # username seems to confuse it?
    use_tls=True
)

# Connection to InfluxDB
influx_address = environ.get('INFLUXDB_ADDRESS', 'localhost')
influx_username = environ.get('INFLUXDB_USERNAME', 'influxdb')
influx_password = environ.get('INFLUXDB_PASSWORD', 'influxdb')
influx_database = environ.get('INFLUXDB_DATABASE', 'fritz.box')
db = InfluxDBClient(
    host=influx_address, username=influx_username,
    password=influx_password
)
db.switch_database(influx_database)

# Get data from FritzBox
data_to_fetch = [
    {'section': 'WANCommonIFC1', 'action': 'GetTotalBytesSent', 'properties': ['NewTotalBytesSent']},
    {'section': 'WANCommonIFC1', 'action': 'GetTotalBytesReceived', 'properties': ['NewTotalBytesReceived']},
    {'section': 'WANIPConn1', 'action': 'GetStatusInfo', 'properties': ['NewUptime']},
    {'section': 'WLANConfiguration1', 'action': 'GetStatistics', 'properties': ['NewTotalPacketsSent', 'NewTotalPacketsReceived']},
    {'section': 'WLANConfiguration2', 'action': 'GetStatistics', 'properties': ['NewTotalPacketsSent', 'NewTotalPacketsReceived']},
    {'section': 'WLANConfiguration3', 'action': 'GetStatistics', 'properties': ['NewTotalPacketsSent', 'NewTotalPacketsReceived']},
    {'section': 'WANDSLInterfaceConfig1', 'action': 'GetInfo', 'properties': [
        'NewUpstreamCurrRate', 'NewDownstreamCurrRate', 'NewUpstreamMaxRate', 'NewDownstreamMaxRate'
    ]},
]

def update_values(fc, db):
    """
    Get the data we're fetching from the FritzConnection and send it to the
    InfluxDB server
    """
    data_points = []
    for row in data_to_fetch:
        try:
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
        # except FritzActionError:
        except Exception as e:
            print(f"Got exception {e} when requesting section {row['section']} action {row['action']} - skipping that now")
        
    
    # print("data_points:", data_points)
    result = db.write_points(data_points)
    print(f"At {time.time():.2f} write_points returned {result}")

def fetch_on_schedule(fc, db, every=20):
    """
    Fetch points every 'every' seconds and send them to the database.
    """
    # Capture the start time before the loop (re)starts so that the loop
    # reentry time is included in our timing.
    start_time = time.time()
    while True:
        update_values(fc, db)
        time.sleep(every - (time.time() - start_time) % every)
        start_time = time.time()

if __name__ == '__main__':
    fetch_on_schedule(fc, db, int(environ.get('FETCH_EVERY', '20')))

