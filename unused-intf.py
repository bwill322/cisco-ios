"""
Look for interfaces with no traffic in a certain amount of time
"""

from __future__ import print_function, unicode_literals
from netmiko import Netmiko
from getpass import getpass
import time
import datetime
import re

def convert_time(x):
    time_seconds = 0
    match = re.search(r'(\d.*)w(\d)d', x)
    if match:
        weeks = int(re.search(r'(\d.*)w(\d)d', x).group(1))
        days = int(re.search(r'(\d.*)w(\d)d', x).group(2))
        time_seconds = weeks * 604800 + days * 86400
    elif ":" in x:
        raw_time = time.strptime(x, '%H:%M:%S')
        time_seconds = datetime.timedelta(
            hours=raw_time.tm_hour,
            minutes=raw_time.tm_min,
            seconds=raw_time.tm_sec
        ).total_seconds()

    return time_seconds

config_cmds = []
hostname = input("Enter hostname: ")
username = input("Enter username: ")

device = {
    'host': hostname,
    'username': username,
    'password': getpass(),
    'device_type': 'cisco_ios'
}

net_connect = Netmiko(**device)

output = net_connect.send_command_timing("show interfaces", use_textfsm=True)

print("-" * 100)
print("Interfaces with no traffic ever or in 3+ weeks")
print("-" * 100)
print("{:30}{:<15}{:<20}{:<15}{:<15}".format(
    "Interface Name",
    "Link Status",
    "Protocol Status",
    "Last Input",
    "Last Output"
    )
)
print("-" * 100)

for i in range(len(output)):
    hardware_type = output[i]['hardware_type']

    intf_name = output[i]['interface']
    last_input = output[i]['last_input']
    last_output = output[i]['last_output']
    link_status = output[i]['link_status']
    protocol_status = output[i]['protocol_status']
    description = output[i]['description']
    last_input_converted = 0
    last_output_converted = 0

    input_never = 'never' in last_input
    output_never = 'never' in last_output

    if not input_never:
        last_input_converted = convert_time(last_input)

    if not output_never:
        last_output_converted = convert_time(last_output)

    #
    activity_check = last_input_converted > 1814400 or last_output_converted > 1814400 or last_output_converted == 0 or last_input_converted == 0

    if 'down' in link_status and 'down' in protocol_status and 'administratively' not in link_status and activity_check:
        print("{:30}{:<15}{:<20}{:<15}{:<15}".format(
            intf_name,
            link_status,
            protocol_status,
            last_input,
            last_output
            )
        )

        description = "description " + description + " [disabled by InactivityChecker]"
        config = "interface " + intf_name + "\n " + description + "\n shutdown\n"
        config_cmds.append(config)

print()
print("-" * 80)
print("Config changes")
print("-" * 80)
for cmds in config_cmds:
    print(cmds)