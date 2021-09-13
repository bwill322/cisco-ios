"""
Look for interfaces with errors
"""

from __future__ import print_function, unicode_literals
from netmiko import Netmiko
from getpass import getpass
from pprint import pprint

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

print("{:25}{:<15}{:<15}{:<15}".format("Interface Name", "Input Errors", "Output Errors", "CRC Errors"))
print("-" * 80)
for i in range(len(output)):
    hardware_type = output[i]['hardware_type']

    if "Ethernet SVI" in hardware_type:
        continue
    elif "RP Management Port" in hardware_type:
        continue
    else:
        intf_name = output[i]['interface']
        input_errors = int(output[i]['input_errors'])
        output_errors = int(output[i]['output_errors'])
        crc_errors = int(output[i]['crc'])

        intf_has_errors = input_errors > 0 or output_errors > 0 or crc_errors > 0

        if intf_has_errors:
            print("{:25}{:<15}{:<15}{:<15}".format(intf_name, input_errors, output_errors, crc_errors))
