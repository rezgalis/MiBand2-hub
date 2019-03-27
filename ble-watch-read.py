import os, sys, time, struct
import ConfigParser as configparser
from datetime import datetime
from base import MiBand2
from constants import ALERT_TYPES, UUIDS
from influxdb import InfluxDBClient

basepath = '/home/pi/MiBand2/'
config = configparser.ConfigParser()
config.read(basepath + 'default.config')

try:
        f = open(basepath + sys.argv[2]+".time", 'r')
        timestamp = int(float(f.read()))
        prev_time = datetime.fromtimestamp(timestamp)
        f.close()
        diff = datetime.now() - prev_time
        if diff.seconds/60 < config.get('DEFAULT','check_frequency'):
                sys.exit(0)
except Exception, e:
        print "File read error?"


print "\nRunning for", sys.argv[1], "-", sys.argv[2]
print "Time:", datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

try:
        band = MiBand2(sys.argv[1], debug=False)
        band.setSecurityLevel(level="medium")
except Exception, e:
        print "Connection failed?"
        #print e
        sys.exit(0)

heartrates = []

client = InfluxDBClient(config.get('DEFAULT','influx_host'), config.get('DEFAULT','influx_port'), config.get('DEFAULT','influx_user'), config.get('DEFAULT','influx_pass'), config.get('DEFAULT','influx_db'))


def get_heartrate():
        band.start_heart_rate_realtime(heart_measure_callback=read_hr)
        json_body = [
                {
                        "measurement": sys.argv[2],
                        "tags": {
                                "sensor": "heartrate"
                        },
                        "time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "fields": {
                                "value": int(round(float(sum(heartrates))/len(heartrates)))
                        }
                }
        ]
        print "Heart rate:", int(round(float(sum(heartrates))/len(heartrates)))
        client.write_points(json_body)


def read_hr(rate):
        heartrates.append(rate)


def get_steps():
        steps_data = band.get_steps()
        json_body = [
                {
                        "measurement": sys.argv[2],
                        "tags": {
                                "sensor": "steps"
                        },
                        "time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "fields": {
                                "value": steps_data['steps']
                        }
                }
        ]
        print "Steps:", steps_data['steps']
        client.write_points(json_body)


def get_distance():
        steps_data = band.get_steps()
        distance_meters = 0
        if steps_data['meters']:
                distance_meters = steps_data['meters']

        json_body = [
                {
                        "measurement": sys.argv[2],
                        "tags": {
                                "sensor": "distance"
                        },
                        "time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "fields": {
                                "value": distance_meters
                        }
                }
        ]
        print "Meters:", distance_meters
        client.write_points(json_body)


def get_battery():
        batt_data = band.get_battery_info()
        json_body = [
                {
                        "measurement": sys.argv[2],
                        "tags": {
                                "sensor": "batt_level"
                        },
                        "time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "fields": {
                                "value": batt_data['level']
                        }
                }
        ]
        print "Battery:", batt_data['level']
        client.write_points(json_body)


def write_time_to_file():
        f = open(basepath + sys.argv[2]+".time", 'w')
        f.write(str(time.time()))
        f.close()


try:
        band.authenticate()
        get_steps()
        get_distance()
        get_heartrate()
        get_battery()
        band.disconnect()
        write_time_to_file()
        sys.exit(0)
except Exception, e:
        print e
        band.disconnect()
        sys.exit(0)
