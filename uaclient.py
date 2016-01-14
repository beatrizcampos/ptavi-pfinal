#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Programa Cliente
"""


import sys
import socket
import hashlib
import os
import time


def hora_actual():

    time_actual = time.time()
    return time.strftime("%Y%m%d%H%M%S", time.gmtime(time_actual))


def fich_log(fichero, evento, ip, puerto, texto):

    fich = open(fichero, 'a')
    hora = fich.write(hora_actual())

    if evento == "sent_to":
        fich.write(" Sent to " + ip
                   + ":" + str(puerto) + ":  " + texto + "\r\n")

    elif evento == "received":
        fich.write(" Received from " + ip + ":"
                   + str(puerto) + ":  " + texto + "\r\n")

    elif evento == "error":
        fich.write(texto + '\r\n')

    elif evento == "starting":
        fich.write(" Starting... \r\n")

    elif evento == "finishing":
        fich.write(" Finishing. \r\n")

    fich.close()


if __name__ == "__main__":
    """
    Cliente UDP simple.
    """
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
    passw = line_account[0].split("=")[2]
    PASSWORD = passw.split(" ")[0][1:-2]
    #IP
    line_uaserver = line[4].split(">")
    uaserver = line_uaserver[0].split("=")[1]
    IP = uaserver.split(" ")[0][1:-1]
    if not IP:
        IP = "127.0.0.1"

    #PUERTO
    uaserver_puerto = line_uaserver[0].split("=")[2]
    PUERTO = uaserver_puerto.split(" ")[0][1:-2]

    #PUERTO RTP
    line_rtpaudio = line[5].split(">")
    rtpaudio = line_rtpaudio[0].split("=")[1]
    PUERTO_RTP = rtpaudio.split(" ")[0][1:-2]

    #IP y PUERTO DEL PROXY
    line_regproxy = line[6].split(">")
    regproxy = line_regproxy[0].split("=")[1]
    IP_PROXY = regproxy.split(" ")[0][1:-1]
    regproxy_puerto = line_regproxy[0].split("=")[2]
    PUERTO_PROXY = regproxy_puerto.split(" ")[0][1:-2]

    #Localizacion Path log
    line_log = line[7].split(">")
    log = line_log[0].split("=")[1]
    PATH_LOG = log.split(" ")[0][1:-2]

    #Localizacion PAth Audio
    line_audio = line[8].split(">")
    audio = line_audio[0].split("=")[1]
    PATH_AUDIO = audio.split(" ")[0][1:-2]

    # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((IP_PROXY, int(PUERTO_PROXY)))

    #METODO REGISTER
    if METHOD == 'REGISTER':
        # Comenzamos a escribir fichero log
        texto = ""
        fich_log(PATH_LOG, "starting", IP, PUERTO, texto)
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
    # Lo escribimos en archivo log
    lista = LINE.split('\r\n')
    texto = " ".join(lista)
    fich_log(PATH_LOG, "sent_to", IP, PUERTO, texto)

    # Recibimos respuesta
    try:
        data = my_socket.recv(1024)
        print("Recibido: \r\n", data.decode('utf-8'))

    except socket.error:
        texto = "Error: No server listening at " + IP_PROXY
        texto += " port " + PUERTO_PROXY
        fich_log(PATH_LOG, "error", IP, PUERTO, texto)
        sys.exit(fich_log)

    # Estudiamos respuesta recibida y la incluimos en ficherolog
    data = data.decode('utf-8').split("\r\n")
    texto = " ".join(data)
    fich_log(PATH_LOG, "received", IP, PUERTO, texto)

    if data[0] == "SIP/2.0 401 Unauthorized":
        # Añadimos cabecera autenticación (FUNCION HASH)
        m = hashlib.md5()
        nonce = data[1].split("=")[-1]
        m.update(bytes(PASSWORD, 'utf-8'))
        m.update(bytes(nonce, 'utf-8'))
        LINE += "Authorization: Digest response=" + m.hexdigest() + "\r\n"
        print("Enviando: \r\n" + LINE)
        my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
        lista = LINE.split('\r\n')
        texto = " ".join(lista)
        fich_log(PATH_LOG, "sent_to", IP, PUERTO, texto)
        data = my_socket.recv(1024)
        print("Recibido: \r\n", data.decode('utf-8'))

    elif data[0] == "SIP/2.0 100 Trying":
        # Metodo de asentimiento. ACK sip:receptor SIP/2.0
        METHOD = 'ACK'
        LINE = METHOD + ' sip:' + OPTION + ' SIP/2.0\r\n'
        print("Enviando: \r\n" + LINE)
        my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
        lista = LINE.split('\r\n')
        texto = " ".join(lista)
        fich_log(PATH_LOG, "sent_to", IP, PUERTO, texto)

        # Envio RTP
        # aEjecutar es un string con lo que se ha de ejecutar en la shell
        IP_RTP = data[9].split(' ')[-2]
        PUERTO_RTP = data[12].split(' ')[-2]
        aEjecutar = "./mp32rtp -i " + IP_RTP + " -p " + PUERTO_RTP
        aEjecutar += " < " + PATH_AUDIO
        print("Vamos a ejecutar", aEjecutar)
        os.system(aEjecutar)

    elif data[0] == "SIP/2.0 200 OK":
        texto = ""
        fich_log(PATH_LOG, "finishing", IP, PUERTO, texto)
        print("Terminando socket...")
        # Cerramos todo
        my_socket.close()
        print("Fin.")
