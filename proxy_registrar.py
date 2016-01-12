#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Programa Proxy
"""


import sys
import socketserver
import socket
import hashlib
import csv
import time


try:
    CONFIG = sys.argv[1]

except IndexError:
    sys.exit("Usage: python proxy_registrar.py config")


class ProxyHandler(socketserver.DatagramRequestHandler):
    """
    Proxy server class
    """
    usuarios_registrados = {}

    def register2file(self):
        """
        Base de datos de usuarios registrados
        """

        fich1 = open(PATH_DATABASE, 'w')
        fich1.write("FICHERO DE TEXTO CON LOS USUARIOS REGISTRADOS\r\n\r\n")
        fich1.write("User\tIP\tPuerto\tFecha de Registro\tExpires\r\n")

        for usuario in self.usuarios_registrados.keys():
            IP = self.usuarios_registrados[usuario][0]
            puerto = self.usuarios_registrados[usuario][1]
            hora_actual = self.usuarios_registrados[usuario][2]
            hora_exp = self.usuarios_registrados[usuario][3]
            fich1.write(usuario + '\t' + IP + '\t' + str(puerto)
                        + '\t' + str(hora_actual) + '\t'
                        + str(hora_exp) + '\r\n')

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
                        self.wfile.write(bytes(answer, 'utf-8') + b'\r\n')
                    elif expires == 0:
                        # Borramos a usuario expirado
                        #del self.usuarios_registrados[direccionsip_client2]
                        print("Borramos: " , direccionsip_usuario)
                        answer = "SIP/2.0 200 OK\r\n "
                        self.wfile.write((bytes(answer, 'utf-8')) + b'\r\n')

                else:
                    # Comprobamos el response
                    direccionsip_client2 = linea_troceada[1].split(':')[1]
                    puerto_client2 = int(linea_troceada[1].split(':')[-1])
                    expires = int(linea_troceada[3].split('\r\n')[0])
                    response = linea_troceada[-1].split('=')[-1]
                    response = response.split('\r')[0]
                    print(direccionsip_client2)
                    print(expires)
                    print(response)
                    m = hashlib.md5()
                    for usuario in passwords_usuarios.keys():
                        if usuario == direccionsip_client2:
                            password = passwords_usuarios[usuario]
                    print(password)
                    m.update(bytes(password, 'utf-8'))
                    m.update(bytes(str(nonce), 'utf-8'))
                    if m.hexdigest() == response:
                        answer = "SIP/2.0 200 OK\r\n\r\n"
                        print("Enviamos :\r\n", answer)
                        self.wfile.write(bytes(answer, 'utf-8') + b'\r\n')
                        #Registramos al usuario
                        #puerto = int(line[1].split(':')[2])
                        hora_actual = time.time()
                        hora_exp = hora_actual + expires
                        informacion = [IP_CLIENT, puerto_client2,
                                       hora_actual, hora_exp]
                        self.usuarios_registrados[direccionsip_client2] = informacion
                        print(self.usuarios_registrados)
                        self.register2file()
                    else:
                        answer = "SIP/2.0 401 Unauthorized\r\n"
                        answer += "WWW Authenticate: nonce="
                        answer += str(nonce) + "\r\n\r\n"
                        self.wfile.write(bytes(answer, 'utf-8') + b'\r\n')

            elif method_client == "INVITE":
                # Enviamos INVITE a destinatorio correspondiente
                linea_troceada = line.decode('utf-8').split(" ")
                destinatario_invite = linea_troceada[1].split(':')[1]
                print("Se lo enviamos a: ", destinatario_invite)
                if destinatario_invite in self.usuarios_registrados:
                    IP_DESTINO = self.usuarios_registrados[destinatario_invite][0]
                    PUERTO_DESTINO = self.usuarios_registrados[destinatario_invite][1]

                    # Creamos socket
                    my_socket = socket.socket(socket.AF_INET,
                                              socket.SOCK_DGRAM)
                    my_socket.setsockopt(socket.SOL_SOCKET,
                                         socket.SO_REUSEADDR, 1)
                    my_socket.connect((IP_DESTINO, int(PUERTO_DESTINO)))
                    my_socket.send(line)
                    data = my_socket.recv(1024)
                    # Reenviamos al cliente
                    self.wfile.write(data)
                else:
                    # Usuario no registrado
                    answer = "SIP/2.0 404 User Not Found\r\n"
                    self.wfile.write(bytes(answer, 'utf-8') + b'\r\n')

            elif method_client == "ACK":
                linea_troceada = line.decode('utf-8').split(" ")
                destino_invite = linea_troceada[1].split(':')[1]
                IP_DESTINO = self.usuarios_registrados[destino_invite][0]
                PUERTO_DESTINO = self.usuarios_registrados[destino_invite][1]
                print("Se lo enviamos a: ", destino_invite)
                print("con IP: ", IP_DESTINO, " y PUERTO: ", PUERTO_DESTINO)
                # Creamos socket
                my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                my_socket.connect((IP_DESTINO, int(PUERTO_DESTINO)))
                my_socket.send(line)

            elif method_client == "BYE":
                linea_troceada = line.decode('utf-8').split(" ")
                destinatario_invite = linea_troceada[1].split(':')[1]
                print("Se lo enviamos a: ", destinatario_invite)
                if destinatario_invite in self.usuarios_registrados:
                    IP_DESTINO = self.usuarios_registrados[destinatario_invite][0]
                    PUERTO_DESTINO = self.usuarios_registrados[destinatario_invite][1]

                    # Creamos socket
                    my_socket = socket.socket(socket.AF_INET,
                                              socket.SOCK_DGRAM)
                    my_socket.setsockopt(socket.SOL_SOCKET,
                                         socket.SO_REUSEADDR, 1)
                    my_socket.connect((IP_DESTINO, int(PUERTO_DESTINO)))
                    my_socket.send(line)
                    data = my_socket.recv(1024)
                    print('Recibimos: \r\n', data.decode('utf-8'))
                    self.wfile.write(data + b'\r\n')

                else:
                    # Usuario no registrado
                    answer = "SIP/2.0 404 User Not Found\r\n"
                    self.wfile.write(bytes(answer, 'utf-8') + b'\r\n')


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
    print("NOMBRE DEL SERVIDOR:  ", NAME_SERVER)
    ip = line_server[0].split("=")[2]
    IP_SERVER = ip.split(" ")[0][1:-1]
    if not IP_SERVER:
        IP_SERVER = "127.0.0.1"
    print("IP DEL SERVIDOR:  ", IP_SERVER)
    puerto = line_server[0].split("=")[3]
    PUERTO_SERVER = puerto.split(" ")[0][1:-2]
    print("PUERTO DEL SERVIDOR:  ", PUERTO_SERVER)

    # Database
    line_database = line[2].split(">")
    database = line_database[0].split("=")[1]
    PATH_DATABASE = database.split(" ")[0][1:-1]
    print(PATH_DATABASE)
    path_password = line_database[0].split("=")[2]
    PASSWORDS_DATABASE = path_password.split("=")[0][1:-2]
    print(PASSWORDS_DATABASE)

    # Fichero Log
    line_log = line[3].split(">")
    log = line_log[0].split("=")[1]
    PATH_LOGSERVER = log.split(" ")[0][1:-2]
    print(PATH_LOGSERVER)

    # LEER FICHERO PASSWORD.TXT , COGER CONTRASEÑAS
    with open(PASSWORDS_DATABASE, newline='') as pwrd_fich:
        lineas = csv.reader(pwrd_fich)
        passwords_usuarios = {}
        for linea in lineas:
            linea_usuario = linea[0].split(':')
            passwords_usuarios[linea_usuario[0]] = linea_usuario[-1]
        print(passwords_usuarios)

    serv = socketserver.UDPServer(((IP_SERVER,
                                    int(PUERTO_SERVER))), ProxyHandler)
    print("Server " + NAME_SERVER + " listening at port "
          + str(PUERTO_SERVER))
    serv.serve_forever()
