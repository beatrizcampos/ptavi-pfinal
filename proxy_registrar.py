#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Programa Proxy
"""


import sys
import socketserver


try:
    CONFIG = sys.argv[1]

except IndexError:
    sys.exit("Usage: python proxy_registrar.py config")


class ProxyHandler(socketserver.DatagramRequestHandler):
    """
    Proxy server class
    """
    Dicc_Users = {}


    def handle(self):
        # Escribe dirección y puerto del cliente (de tupla client_address)
        IP_CLIENT = str(self.client_address[0])
        print("LA IP DEL CLIENTE ES: " + IP_CLIENT)
        nonce = 898989898798989898989
        #self.wfile.write(b"Hemos recibido tu peticion")
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            method_client = line.decode('utf-8').split(' ')[0]
            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break
            print("El cliente nos manda: \r\n" + line.decode('utf-8'))

            if method_client == "REGISTER":
                linea_troceada = line.decode('utf-8').split(" ")
                print(len(linea_troceada))
                print(linea_troceada[0])
                print(linea_troceada[1])
                print(linea_troceada[2])
                print(linea_troceada[3])
                print(linea_troceada[-1])

                if len(linea_troceada) == 4:
                    # Enviamos: SIP/2.0 401 Unauthorized
                    direccionsip_usuario = linea_troceada[1].split(':')[1]
                    expires = int(linea_troceada[-1])
                    puerto_cliente = (linea_troceada[1].split(':')[-1])
                    print(direccionsip_usuario)
                    print(expires)
                    print(puerto_cliente)
                    if expires > 0:
                        answer = ("SIP/2.0 401 Unauthorized" + '\r\n')
                        answer += "WWW Authenticate: nonce="
                        answer += str(nonce) + "\r\n\r\n"
                        self.wfile.write(bytes(answer, 'utf-8'))

                  #else:
                    # compreba el response

        

if __name__ == "__main__":
    """
    Creamos servidor eco y escuchamos
    """

    # Abrimos fichero xml para coger informacion
    fich = open(CONFIG, 'r')
    line = fich.readlines()
    fich.close()

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

    # LEER FICHERO PASSWORD.TXT
    # COGES LAS CONTRASEÑAS
    
    serv = socketserver.UDPServer(((IP_SERVER, int(PUERTO_SERVER))), ProxyHandler)
    print("Server " + NAME_SERVER +  " listening at port " + str(PUERTO_SERVER))
    serv.serve_forever()



