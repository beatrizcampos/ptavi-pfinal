#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Programa cliente
"""


import sys

try:
    CONFIG = sys.argv[1]
    METHOD = sys.argv[2]
    OPTION = sys.argv[3]

except IndexError:
    print("Usage: python uaclient.py config method option")

# Abrimos fichero xml para coger informacion
fich = open(CONFIG, 'r')
line = fich.readlines()
fich.close()

line_account = line[3].split(">")
account = line_account[0].split("=")[1]
USERNAME = account.split(" ")[0][1:-1]
print("imprimimos linea account" )
print(line_account)
print(account)
print(USERNAME)
