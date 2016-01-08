#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Programa Proxy
"""


import sys

try:
    CONFIG = sys.argv[1]

except IndexError:
    print("Usage: python proxy_registrar.py config")

print("Server ServidorFamilySimpson listening at port 5555")
