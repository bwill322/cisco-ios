"""
Update an interface and change the macro applied to it
"""


from __future__ import print_function, unicode_literals
import os
import signal
from netmiko import Netmiko
import login_tools

signal.signal(signal.SIGINT, signal.SIG_DFL)  # KeyboardInterrupt: Ctrl-C


def make_changes(data):
    """
    :param data: list of config changes to make
    :return: nothing
    """

    if len(data) > 0:
        if os.path.exists("config-changes.txt"):
            os.remove("config-changes.txt")
            print("Removed old config-changes.txt file")
        else:
            print("No previous config-changes.txt file found, proceeding...")

        with open("config-changes.txt", mode="a", encoding="utf8") as file:
            for cmd in data:
                file.write(cmd)

        print("Pushing changes to device...")
        net_connect.send_config_set(data)
        print("Changes made, saving config...")
        save_config = net_connect.send_command_timing("copy running-config startup-config")
        if "Destination filename [startup-config]" in save_config:
            net_connect.send_command_timing("\n")
            print("Saved device configuration")
        print("-" * 80)


netmiko_exceptions = (netmiko.ssh_exception.NetmikoAuthenticationException,
                      netmiko.ssh_exception.NetmikoTimeoutException)

hostname = login_tools.get_input("Enter hostname: ")
username, password = login_tools.get_credentials()
port_descr = input("Port Description: ")
new_macro = input("Macro to Apply: ")

device = {
    'host': hostname,
    'username': username,
    'password': password,
    'device_type': 'cisco_ios'
}
try:
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
                make_changes(config_changes)

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
except netmiko_exceptions as e:
    print("Failed to: ", hostname, e)
