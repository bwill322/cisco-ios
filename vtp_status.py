"""
Check VTP status on a Cisco IOS/IOS-XE switch
"""

from __future__ import print_function, unicode_literals

from netmiko import Netmiko
import login_tools
import netbox_tools
import signal

signal.signal(signal.SIGINT, signal.SIG_DFL)  # KeyboardInterrupt: Ctrl-C

device_role = login_tools.get_input("Enter device type: ")
print("-" * 80)
device_list = netbox_tools.get_device_by_role(device_role)

username, password = login_tools.get_credentials()

for device in device_list:
    hostname = device

    current_device = {
        'host': hostname,
        'username': username,
        'password': password,
        'device_type': 'cisco_ios'
    }

    net_connect = Netmiko(**current_device)

    output = net_connect.send_command_timing("show vtp status", use_textfsm=True)

    vtp_mode = output[0]['mode']

    print("VTP Mode on {} is {}".format(hostname, vtp_mode))

