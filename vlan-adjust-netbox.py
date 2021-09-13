from netmiko import Netmiko
from extras.scripts import *

'''
A script which generates configuration to remove VLAN config on ports

Script is adapted to run from within Netbox
'''


class RemoveVlan(Script):
    class Meta:
        name = "Remove VLAN from Trunk  Interface"
        description = "Generates config to remove VLAN from a trunk interface"
        commit_default = False

    vlan_change = IntegerVar(label="Enter VLAN ID", required=True)
    host = StringVar(label="Enter hostname: ", required=True)
    def run(self, data, commit):
        host = data['host']
        vlan_change = data['vlan_change']
        device = {
            'host': host,
            'username': '',
            'password': '',
            'device_type': 'cisco_ios'
        }
        net_conn = Netmiko(**device)
        show_vlan_output = net_conn.send_command_timing("show vlan", use_textfsm=True)

        output = 'Config Changes\n'

        for i in range(len(show_vlan_output)):
            vlan_id = int(show_vlan_output[i]['vlan_id'])
            if vlan_id == vlan_change:
                interfaces = show_vlan_output[i]['interfaces']
                for interface in interfaces:
                    output = output + 'interface ' + interface + '\n switchport trunk allowed vlan remove ' + str(vlan_change) + '\n'

        return(output)
