# MiBand2-hub
Python script to automate reading of MiBand2 watch data on regular intervals and sending it to InfluxDB

### How this works ###
a crontab job is scheduled to run every 5 minutes which calls this script with two parameters - BLE address of the device and friendly name of the device (which is used to submit data to InfluxDB)
Data from watch is read every 15minutes; if watch is not nearby, script will try to communicate with watch every 5minutes (crontab) until successful - then it reads data every 15minutes again.
Timestamp of last successful data read from watch is saved to <<WATCH_FRIENDLY_NAME>>.time
Config with InfluxDB credentials is saved locally.

### Prerequisites ###
Awesome work by creotiv: https://github.com/creotiv/MiBand2
Python client for InfluxDB: https://github.com/influxdata/influxdb-python
(please follow instructions for installation of the above two - that should suffice)

#### Sample cron job ####
```sh
#!/bin/bash
#cron job for reading fitness watch data to InfluxDB

sudo hciconfig hci0 down
sudo hciconfig hci0 up
sudo python /home/pi/MiBand2/ble-watch-read.py 00:00:00:00:00:00 hr_watch_mom
sudo hciconfig hci0 down
```

#### Sample config file (default.config) ####
```python
[DEFAULT]
#frequency of reading watch data (minutes)
check_frequency = 15

#Influx DB params
influx_host = myweb.com
influx_port = 8086
influx_user = myuser
influx_pass = mypass
influx_db = mydb

```
