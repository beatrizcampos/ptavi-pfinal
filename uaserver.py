#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Programa User Agent Server
"""


import sys
import socketserver
import socket
import os
import time
from uaclient import hora_actual
from uaclient import fich_log


class ProxyHandler(socketserver.DatagramRequestHandler):
    """
    Proxy server class
    """
    RTP = {'ip': '', 'puerto': 0}

    def handle(self):
        # Escribe dirección y puerto del cliente (de tupla client_address)
        IP_CLIENT = str(self.client_address[0])
        PUERTO_CLIENT = int(self.client_address[1])
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            method_client = line.decode('utf-8').split(' ')[0]
            linea_deco = line.decode('utf-8').split(' ')
            #Incluimos lo recibido en fichero log
            texto = " ".join(line.decode('utf-8').split("\r\n"))
            fich_log(PATH_LOG, "received", IP_CLIENT, PUERTO_CLIENT, texto)

            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break

            print("El cliente nos manda: \r\n" + line.decode('utf-8'))
            if not method_client in methods:
                answer = ("SIP/2.0 405 Method Not Allowed" + '\r\n\r\n')
                self.wfile.write(bytes(answer, 'utf-8'))

            elif method_client == "INVITE":
                # Mandamos código respuesta
                IP_RTPDESTINO = linea_deco[4].split("\r\n")[0]
                PUERTO_RTPDESTINO = linea_deco[7].split(" ")[-1]

                self.RTP["ip"] = IP_RTPDESTINO
                self.RTP["puerto"] = PUERTO_RTPDESTINO
                answer = ("SIP/2.0 100 Trying" + '\r\n\r\n' +
                          "SIP/2.0 180 Ringing" + '\r\n\r\n' +
                          "SIP/2.0 200 OK" + '\r\n\r\n')
                answer += "Content-Type: application/sdp\r\n\r\n"
                answer += "v=0\r\n" + "o=" + USERNAME + " " + IP + " \r\n"
                answer += "s=SIP's PARTY" + "\r\n" + "t=0" + "\r\n"
                answer += "m=audio " + PUERTO_RTP + " RTP" + "\r\n"
                print(" Codigo respuesta a INVITE:  \r\n", answer)
                self.wfile.write(bytes(answer, 'utf-8'))
                lista = answer.split('\r\n')
                texto = " ".join(lista)
                fich_log(PATH_LOG, "sent_to", IP_CLIENT, PUERTO_CLIENT, texto)

            elif method_client == "BYE":
                answer = "SIP/2.0 200 OK\r\n"
                print(" Codigo respuesta a BYE:  \r\n", answer)
                self.wfile.write(bytes(answer, 'utf-8'))
                lista = answer.split('\r\n')
                texto = " ".join(lista)
                fich_log(PATH_LOG, "sent_to", IP_CLIENT, PUERTO_CLIENT, texto)

            elif method_client == "ACK":
                #Comenzamos envio RTP
                aEjecutar = "./mp32rtp -i " + self.RTP["ip"]
                aEjecutar += " -p " + self.RTP["puerto"]
                aEjecutar += " < " + PATH_AUDIO
                print("Vamos a ejecutar", aEjecutar)
                os.system(aEjecutar)

            else:
                answer = ("SIP/2.0 400 Bad Request" + '\r\n\r\n')
                self.wfile.write(bytes(answer, 'utf-8'))
                lista = answer.split('\r\n')
                texto = " ".join(lista)
                fich_log(PATH_LOG, "sent_to", IP_CLIENT, PUERTO_CLIENT, texto)


if __name__ == "__main__":

    try:
        CONFIG = sys.argv[1]

    except IndexError:
        sys.exit("Usage: python uaserver.py config")

    print("Listening...")

    methods = ['INVITE', 'ACK', 'BYE']
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

    serv = socketserver.UDPServer(((IP, int(PUERTO))), ProxyHandler)
    serv.serve_forever()
