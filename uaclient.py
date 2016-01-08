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
