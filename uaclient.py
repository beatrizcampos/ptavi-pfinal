#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Programa Cliente
"""


import sys
import socket
import hashlib

try:
    CONFIG = sys.argv[1]
    METHOD = sys.argv[2]
    OPTION = sys.argv[3]

except IndexError:
    sys.exit("Usage: python uaclient.py config method option")

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
if not IP:
    IP = "127.0.0.1"
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


# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((IP_PROXY, int(PUERTO_PROXY)))


#METODO REGISTER
if METHOD == 'REGISTER':
    LINE = METHOD + ' sip:' + USERNAME + ':' + PUERTO + ' SIP/2.0\r\n'
    LINE += "Expires: " + OPTION + "\r\n"

elif METHOD == 'INVITE':
    # Añadimos cabeceras
    LINE = "INVITE " + "sip:" + OPTION + " SIP/2.0\r\n"
    LINE += "Content-Type: application/sdp\r\n\r\n"
    LINE += "v=0\r\n" + "o=" + USERNAME + " " + IP + " \r\n"
    LINE += "s=SIP's PARTY" + "\r\n" + "t=0" + "\r\n"
    LINE += "m=audio " + PUERTO_RTP + " RTP" + "\r\n"

elif METHOD == 'BYE':
    #BYE sip:receptor SIP/2.0
    LINE = METHOD + " sip:" + OPTION + " SIP/2.0\r\n"

# Enviamos la petición
print("Enviando: \r\n" + LINE)
my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
# Recibimos respuesta
data = my_socket.recv(1024)
print("Recibido: \r\n", data.decode('utf-8'))


# Estudiamos respuesta
data = data.decode('utf-8').split("\r\n")

if data[0] == "SIP/2.0 401 Unauthorized":
    # Añadimos cabecera autenticación (FUNCION HASH)
    m = hashlib.md5()
    nonce = data[1].split("=")[-1]
    print(nonce)
    m.update(bytes(PASSWORD, 'utf-8'))
    m.update(bytes(nonce, 'utf-8'))
    LINE += "Authorization: response=" + m.hexdigest() + "\r\n"
    print("Enviando: \r\n" + LINE)
    my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
    data = my_socket.recv(1024)
    print(data.decode('utf-8'))

elif data[0] == "SIP/2.0 100 Trying":
    # Metodo de asentimiento. ACK sip:receptor SIP/2.0
    METHOD = 'ACK'
    LINE = METHOD + ' sip:' + OPTION + ' SIP/2.0\r\n'
    print("Enviando: \r\n" + LINE)
    my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
