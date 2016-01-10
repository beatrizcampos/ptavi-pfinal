#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Programa User Agent Server
"""


import sys
import socket

try:
    CONFIG = sys.argv[1]

except IndexError:
    sys.exit("Usage: python uaserver.py config")



if __name__ == "__main__":
    # Abrimos fichero xml para coger informacion
    fich = open(CONFIG, 'r')
    line = fich.readlines()
    fich.close()

#Conseguimos nombre de usuario y contraseña (linea 3-xml)
line_account = line[3].split(">")
account = line_account[0].split("=")[1]
USERNAME = account.split(" ")[0][1:-1]
print("imprimimos nombre:   ", USERNAME)
passw = line_account[0].split("=")[2]
PASSWORD = passw.split(" ")[0][1:-2]
print("imprimimos contraseña:   ", PASSWORD)
#IP
line_uaserver = line[4].split(">")
uaserver = line_uaserver[0].split("=")[1]
IP = uaserver.split(" ")[0][1:-1]
print("Imprimimos IP:   ", IP)

#PUERTO
uaserver_puerto = line_uaserver[0].split("=")[2]
PUERTO = uaserver_puerto.split(" ")[0][1:-2]
print("Imprimimos PUERTO:   ", PUERTO)

#PUERTO RTP
line_rtpaudio = line[5].split(">")
rtpaudio = line_rtpaudio[0].split("=")[1]
PUERTO_RTP = rtpaudio.split(" ")[0][1:-2]
print("Imprimimos PUERTO RTP:   ", PUERTO_RTP)

#IP y PUERTO DEL PROXY
line_regproxy = line[6].split(">")
regproxy = line_regproxy[0].split("=")[1]
IP_PROXY = regproxy.split(" ")[0][1:-1]
print("Imprimimos IP DEL Proxy:   ", IP_PROXY)
regproxy_puerto = line_regproxy[0].split("=")[2]
PUERTO_PROXY = regproxy_puerto.split(" ")[0][1:-2]
print("Imprimimos Puerto DEL Proxy:   ", PUERTO_PROXY)


#Localizacion Path log
line_log = line[7].split(">")
log = line_log[0].split("=")[1]
PATH_LOG = log.split(" ")[0][1:-2]
print(PATH_LOG)

#Localizacion PAth Audio
line_audio = line[8].split(">")
audio = line_audio[0].split("=")[1]
PATH_AUDIO = audio.split(" ")[0][1:-2]
print(PATH_AUDIO)
