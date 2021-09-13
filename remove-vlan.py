from __future__ import print_function, unicode_literals

'''
Read input from stdin and produce some commands to remove a vlan
'''

vlan = input("Enter a VLAN ID: ")

with open("show_vlan.txt") as f:
    output = f.read()

output = output.split()
print("-" * 80)
for entry in output:
    if entry.startswith("Ports"):
        continue

    if entry.startswith("Gi"):
        entry = entry.strip(",")
        print("interface {}\n switchport trunk allowed vlan remove {}".format(entry,vlan))
    elif entry.startswith("Po"):
        print("interface {}\n switchport trunk allowed vlan remove {}".format(entry,vlan))