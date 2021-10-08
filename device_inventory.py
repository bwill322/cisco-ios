"""
Login to device, run show inventory and show version to get current info for replacement
"""

from __future__ import print_function, unicode_literals
import signal
import netmiko.ssh_exception
from netmiko import Netmiko
import login_tools
from getpass import getpass
import sys

signal.signal(signal.SIGINT, signal.SIG_DFL)  # KeyboardInterrupt: Ctrl-C

with open(sys.argv[1]) as f:
    device_list = f.read().splitlines()

print("-" * 100)
print("Devices working with:")
print("-" * 100)
for device in device_list:
    print(device)
print("-" * 100)
username = login_tools.get_input("Enter username to use for all devices: ")
print("-" * 100)

for hostname in device_list:
    print("Current device: ", hostname)
    device = {
        'host': hostname,
        'username': username,
        'password': getpass(),
        'device_type': 'cisco_ios'
    }

    netmiko_exceptions = (netmiko.ssh_exception.NetmikoAuthenticationException,
                          netmiko.ssh_exception.NetmikoTimeoutException)

    try:
        net_connect = Netmiko(**device)
        inventory = net_connect.send_command("show interface description")

        print("-" * 100)
        print("Device: ", hostname)
        print(inventory)
        print("-" * 100)
    except netmiko_exceptions as e:
        print("Failed to: ", hostname, e)
