"""
Get input from user
"""

from __future__ import print_function, unicode_literals

from getpass import getpass


def get_input(prompt=''):
    """
    :param prompt: the prompt for the data entry
    :return: the data entered
    """
    try:
        line = raw_input(prompt)
    except NameError:
        line = input(prompt)
    return line


def get_credentials():
    """
    :return: the username and password
    """
    username = get_input("Enter username: ")
    password = getpass()

    return username, password
