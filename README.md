# fritz_to_influx
A Python program for polling a Fritz!Box router and sending useful metrics to an Influx database

# Installation

`$ pipenv install`

# Usage

The credentials for both the Fritz!BOX and InfluxDB are set via environment
variable.  This allows them to be set via a script and not be visible in
`ps` or other process information:

* `FRITZBOX_ADDRESS`: The address of the Fritz!BOX.  Defaults to 169.254.1.1`,
   which Fritz!BOX devices listen on.
* `FRITZBOX_USERNAME`: The admin username of the Fritz!BOX.  Defaults to
   'admin.'
* `FRITZBOX_PASSWORD`: The admin password of the Fritz!BOX.  Defaults to
   'admin'.
* `INFLUXDB_ADDRESS`: The IP address of the InfluxDB server.  Defaults to
   'localhost'.
* `INFLUXDB_USERNAME`: The username for access to the InfluxDB server.
   Defaults to 'influxdb'.
* `INFLUXDB_PASSWORD`: The password for access to the InfluxDB server.
   Defaults to 'influxdb'.
* `INFLUXDB_DATABASE`: The database to put data into in the InfluxDB server.
   Defaults to 'fritz.box'.
 
TLS is used to connect to the Fritz!BOX by default.

The following data is read:

- Section 'WANCommonIFC' action 'GetTotalBytesSent' properties: 'NewTotalBytesSent'
- Section 'WANCommonIFC' action 'GetTotalBytesReceived' properties 'NewTotalBytesReceived'
- Section 'WANIPConn' action 'GetStatusInfo' properties 'NewUptime'
- Section 'WLANConfiguration1' action 'GetStatistics' properties 'NewTotalBytesSent', 'NewTotalPacketsReceived'
- Section 'WLANConfiguration2' action 'GetStatistics' properties 'NewTotalBytesSent', 'NewTotalPacketsReceived'
- Section 'WLANConfiguration3' action 'GetStatistics' properties 'NewTotalBytesSent', 'NewTotalPacketsReceived'

Data is read every `20` seconds, or as defined by the `FETCH_EVERY` environment
variable.  Exit the program by Ctrl-C or other signal.
