from __future__ import print_function, unicode_literals
from netmiko import Netmiko
from getpass import getpass


'''
A script which generates configuration to remove VLAN config on ports
'''

try:
    vlan_change = raw_input("Enter VLAN ID: ")
    host = raw_input("Enter hostname: ")
    username = raw_input("Enter username:")
except NameError:
    vlan_change = input("Enter VLAN ID: ")
    host = input("Enter hostname: ")
    username = input("Enter username: ")

vlan_change = int(vlan_change)

device = {
    'host': host,
    'username': username,
    'password': getpass(),
    'device_type': 'cisco_ios'
}
net_conn = Netmiko(**device)
show_vlan_output = net_conn.send_command_timing("show vlan", use_textfsm=True)

print()
print('-' * 80)
for i in range(len(show_vlan_output)):
    vlan_id = int(show_vlan_output[i]['vlan_id'])
    if vlan_id == vlan_change:
        interfaces = show_vlan_output[i]['interfaces']
        for interface in interfaces:
            print('interface {}\n switchport trunk allowed vlan remove {}\n'.format(interface, vlan_change))
print('-' * 80)
print()
