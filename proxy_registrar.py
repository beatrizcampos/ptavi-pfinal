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

print()
# NOMBRE ; PUERTO ; IP del Servidor donde escuchara
line_server = line[1].split(">")
server = line_server[0].split("=")[1]
NAME_SERVER = server.split(" ")[0][1:-1]
print("NOMBRE DEL SERVIDOR:  " ,NAME_SERVER)
ip = line_server[0].split("=")[2]
IP_SERVER = ip.split(" ")[0][1:-1]
print("IP DEL SERVIDOR:  ",IP_SERVER)
puerto = line_server[0].split("=")[3]
PUERTO_SERVER = puerto.split(" ")[0][1:-2]
print("PUERTO DEL SERVIDOR:  ",PUERTO_SERVER)

# Database
line_database = line[2].split(">")
database = line_database[0].split("=")[1]
PATH_DATABASE = database.split(" ")[0][1:-2]
print(PATH_DATABASE)

# Fichero Log
line_log = line[3].split(">")
log = line_log[0].split("=")[1]
PATH_LOGSERVER = log.split(" ")[0][1:-2]
print(PATH_LOGSERVER)

