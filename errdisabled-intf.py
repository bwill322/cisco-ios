"""
Look for interfaces with status of err-disabled
"""

from __future__ import print_function, unicode_literals

import time
import datetime
import re
import os
from getpass import getpass
from netmiko import Netmiko

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
print("Hostname: " + hostname)
print("-" * 100)
print("Err-disabled Interfaces")
print("-" * 100)
print("{:30}{:<15}".format(
    "Interface Name",
    "Protocol Status",
    )
)
print("-" * 100)

for i, element in enumerate(output):
    hardware_type = output[i]['hardware_type']

    intf_name = output[i]['interface']
    protocol_status = output[i]['protocol_status']
    description = output[i]['description']

    # interface is error disabled
    err_disabled = 'err-disabled' in protocol_status

    if err_disabled:
        print("{:30}{:<15}".format(
            intf_name,
            protocol_status,
            )
        )

