import subprocess
import os
import json
from time import gmtime, strftime
from influxdb import InfluxDBClient
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


host = '1.1.1.1'
port = 8086
user = 'laurent'
password = '123456'
dbname = 'dhcp'
ssl = True
check_ssl = False

influxdb_client = InfluxDBClient(host, port, user, password, dbname, ssl, check_ssl)

class Subnet:
    range_ip = ""
    defined_ip = ""
    used_ip = ""
    free_ip = ""
    free_percent = ""
    used_percent = ""

    def __init__(self, range_ip, defined_ip, used_ip, free_ip, free_percent, used_percent):
        self.range_ip = range_ip
        self.defined_ip = defined_ip
        self.used_ip = used_ip
        self.free_ip = free_ip
        self.free_percent = free_percent
        self.used_percent = used_percent

json_output = subprocess.Popen(['dhcpd-pools', '-c', '/etc/dhcp/dhcpd.conf', '-f', 'j'], stdout=subprocess.PIPE).communicate()[0]
dhcp_json_output = json.loads(json_output)

dhcp_summary = dhcp_json_output['summary']
total_defined_ip = dhcp_summary['defined']
total_used_ip = dhcp_summary['used']
free_ip = dhcp_summary['free']

used_percent = 100 * float(dhcp_summary['used']) / float(dhcp_summary['defined'])
free_percent = 100 * float(dhcp_summary['free']) / float(dhcp_summary['defined'])

current_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

json_body_1 = [
    {
        "measurement": "Total IP",
        "tags": {
            "host": "dhcp1",
        },
        "time": current_time,
        "fields": {
            "value": total_defined_ip,
        }
    }
]

json_body_2 = [
    {
        "measurement": "Total used IP",
        "tags": {
            "host": "dhcp1",
        },
        "time": current_time,
        "fields": {
            "value": total_used_ip,
        }
    }
]

json_body_3 = [
    {
        "measurement": "Total free IP",
        "tags": {
            "host": "dhcp1",
        },
        "time": current_time,
        "fields": {
            "value": free_ip,
        }
    }
]

json_body_4 = [
    {
        "measurement": "Total free percent",
        "tags": {
            "host": "dhcp1",
        },
        "time": current_time,
        "fields": {
            "value": free_percent,
        }
    }
]

json_body_5 = [
    {
        "measurement": "Total usedpercent",
        "tags": {
            "host": "dhcp1",
        },
        "time": current_time,
        "fields": {
            "value": used_percent,
        }
    }
]



#print("Write points: {0}".format(json_body_1))
influxdb_client.write_points(json_body_1)
influxdb_client.write_points(json_body_2)
influxdb_client.write_points(json_body_3)
influxdb_client.write_points(json_body_4)
influxdb_client.write_points(json_body_5)
#print total_defined_ip
#print total_used_ip
#print free_ip
#print used_percent
#print free_percent

for subnet in dhcp_json_output['subnets']:
    subnet_percent_used = 100 * float(dhcp_summary['used']) / float(dhcp_summary['defined'])
    subnet_percent_free = 100 * float(dhcp_summary['free']) / float(dhcp_summary['defined'])
    json_body_subnet_1 = [
        {
            "measurement": "Range",
            "tags": {
                "host": subnet['location'],
            },
            "time": current_time,
            "fields": {
                "value": subnet['range'],
            }
        }
    ]
    json_body_subnet_2 = [
        {
            "measurement": "Defined",
            "tags": {
                "host": subnet['location'],
            },
            "time": current_time,
            "fields": {
                "value": subnet['defined'],
            }
        }
    ]
    json_body_subnet_3 = [
        {
            "measurement": "Used",
            "tags": {
                "host": subnet['location'],
            },
            "time": current_time,
            "fields": {
                "value": subnet['used'],
            }
        }
    ]
    json_body_subnet_4 = [
        {
            "measurement": "Free",
            "tags": {
                "host": subnet['location'],
            },
            "time": current_time,
            "fields": {
                "value": subnet['free'],
            }
        }
    ]
    json_body_subnet_5 = [
        {
            "measurement": "Subnet Percent Used",
            "tags": {
                "host": subnet['location'],
            },
            "time": current_time,
            "fields": {
                "value": subnet_percent_used,
            }
        }
    ]
    json_body_subnet_6 = [
        {
            "measurement": "Subnet Percent Free",
            "tags": {
                "host": subnet['location'],
            },
            "time": current_time,
            "fields": {
                "value": subnet_percent_free,
            }
        }
    ]
    influxdb_client.write_points(json_body_subnet_1)
    influxdb_client.write_points(json_body_subnet_2)
    influxdb_client.write_points(json_body_subnet_3)
    influxdb_client.write_points(json_body_subnet_4)
    influxdb_client.write_points(json_body_subnet_5)
    influxdb_client.write_points(json_body_subnet_6)
    #print subnet['range']
    #print subnet['defined']
    #print subnet['used']
    #print subnet['free']



#    vl.dispatch(type='count', type_instance='total',
#                values=[subnet['defined']])
#    vl.dispatch(type='count', type_instance='used',
#                values=[subnet['used']])
#    vl.dispatch(type='count', type_instance='free',
#                values=[subnet['free']])
#    used_percent = 100 * float(subnet['used'])/float(subnet['defined'])
#    vl.dispatch(type='percent', type_instance='used_percent',
#                values=[used_percent])
#    free_percent = 100 * float(subnet['free']) / float(subnet['defined'])
#    vl.dispatch(type='percent', type_instance='free_percent',
#                values=[free_percent])
