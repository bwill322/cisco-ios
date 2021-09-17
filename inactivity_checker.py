"""
Look for interfaces with no traffic in a certain amount of time
"""

from __future__ import print_function, unicode_literals

import time
import datetime
import re
import os
from getpass import getpass
from netmiko import Netmiko


def convert_time(data):
    """
    :param data: raw last input or output time from network device
    :return: time in seconds
    """
    time_seconds = 0
    match = re.search(r'(\d.*)w(\d)d', data)
    if match:
        weeks = int(re.search(r'(\d.*)w(\d)d', data).group(1))
        days = int(re.search(r'(\d.*)w(\d)d', data).group(2))
        time_seconds = weeks * 604800 + days * 86400
    elif ":" in data:
        raw_time = time.strptime(data, '%H:%M:%S')
        time_seconds = datetime.timedelta(
            hours=raw_time.tm_hour,
            minutes=raw_time.tm_min,
            seconds=raw_time.tm_sec
        ).total_seconds()

    return time_seconds


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
        net_connect.send_config_from_file("config-changes.txt")
        print("Changes above made and interfaces disabled")
        save_config = net_connect.send_command_timing("copy running-config startup-config")
        if "Destination filename [startup-config]" in save_config:
            net_connect.send_command_timing("\n")
            print("Saved device configuration")
        print("-" * 80)


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
print("Hostname: " + hostname)
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

for i, element in enumerate(output):
    hardware_type = output[i]['hardware_type']

    intf_name = output[i]['interface']
    last_input = output[i]['last_input']
    last_output = output[i]['last_output']
    link_status = output[i]['link_status']
    protocol_status = output[i]['protocol_status']
    description = output[i]['description']
    LAST_INPUT_CONVERTED = 0
    LAST_OUTPUT_CONVERTED = 0

    # check if the last input/output is never
    input_never = 'never' in last_input
    output_never = 'never' in last_output
    both_never = input_never and output_never

    # convert last input/output to seconds as long as never isn't the value
    if not input_never:
        LAST_INPUT_CONVERTED = convert_time(last_input)
    if not output_never:
        LAST_OUTPUT_CONVERTED = convert_time(last_output)

    # if VLAN is in the interface name, interface is skipped
    intf_is_svi = 'Vlan' in intf_name

    # if "inactivity-ignore" is present in interface description, interface is skipped
    ignore_intf = 'inactivity-ignore' in description

    # if interface is admin down, interface is skipped
    admin_down = 'administratively' in link_status

    # if last in/out packet was greater than 3 weeks ago or both are never,
    # interface is eligible to be shutdown
    last_activity_threshold = LAST_INPUT_CONVERTED > 1814400 \
        or LAST_OUTPUT_CONVERTED > 1814400 or both_never

    # if link and protocol status are down, interface is eligible to be shutdown
    down_down = 'down' in link_status and 'down' in protocol_status

    # print out details on interface if conditions met
    if down_down and last_activity_threshold and \
            not intf_is_svi and not admin_down and not ignore_intf:
        print("{:30}{:<15}{:<20}{:<15}{:<15}".format(
            intf_name,
            link_status,
            protocol_status,
            last_input,
            last_output
            )
        )

        intf_disabled_before = re.search(r"(.*)(\[disabled by InactivityChecker])", description)
        if intf_disabled_before:
            desc_group0 = intf_disabled_before.group(0).strip()
            desc_group1 = intf_disabled_before.group(1).strip()
            if desc_group0 == "[disabled by InactivityChecker]":
                description = ""
            else:
                description = desc_group1

        description = "description " + description + " [disabled by InactivityChecker]"
        config = "interface " + intf_name + "\n " + description + "\n shutdown\n"
        config_cmds.append(config)

if len(config_cmds) > 0:
    print()
    print("-" * 80)
    print("Config changes")
    print("-" * 80)
    for cmds in config_cmds:
        print(cmds)

    proceed_with_changes = input("Would you like to make the changes? [y/n] ")
    SHOULD_WE_PROCEED = True

    while SHOULD_WE_PROCEED:
        if proceed_with_changes == "y":
            make_changes(config_cmds)
            print("Exiting out...")
            SHOULD_WE_PROCEED = False
        elif proceed_with_changes == "n":
            SHOULD_WE_PROCEED = False
            print("Exiting out...")
        else:
            proceed_with_changes = input("Please enter either y or n: ")
else:
    print()
    print("-" * 80)
    print("No config changes to make")
    print("-" * 80)
