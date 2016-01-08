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

# Abrimos fichero xml para coger informacion
fich = open(CONFIG, 'r')
line = fich.readlines()
fich.close()

# NOMBRE ; PUERTO ; IP del Servidor donde escuchara
line_sever = line[2].split(">")
print(line_sever)

