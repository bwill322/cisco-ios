"""
Update an interface and change the macro applied to it
"""


from __future__ import print_function, unicode_literals
from netmiko import Netmiko
from getpass import getpass

hostname = input("Enter hostname: ")
username = input("Enter username: ")
port_descr = input("Port Description: ")
new_macro = input("Macro to Apply: ")

device = {
    'host': hostname,
    'username': username,
    'password': getpass(),
    'device_type': 'cisco_ios'
}

net_connect = Netmiko(**device)

output = net_connect.send_command_timing("show interfaces", use_textfsm=True)

print()
print("-" * 80)
print("{:<30}{:<30}".format(
    "Interface Name",
    "Description"
    )
)
print("-" * 80)

for i in range(len(output)):
    intf_name = output[i]['interface']
    description = output[i]['description']

    if port_descr in description:
        print("{:<30}{:<30}".format(intf_name, description))
        command = "show running-config interface " + intf_name
        intf_running_config = net_connect.send_command_timing(command)
        print()
        print("-" * 80)
        print("Current Interface Config")
        print("-" * 80)
        print(intf_running_config)

        config_changes = [
            'default interface ' + intf_name,
            'interface ' + intf_name,
            'description ' + description,
            'macro apply ' + new_macro
        ]

        proceed = input("Proceed with changes? [y/n]: ")

        if 'y' in proceed:
            print()
            print("-" * 80)
            print("Pushing Interface Change....")
            print("-" * 80)
            net_connect.send_config_set(config_changes)

            print()
            print("-" * 80)
            print("New Interface Config....")
            print("-" * 80)
            intf_running_config = net_connect.send_command_timing(command)
            print(intf_running_config)
            break
        else:
            print()
            print("-" * 80)
            print("Exiting out, making no changes")
            print("-" * 80)
