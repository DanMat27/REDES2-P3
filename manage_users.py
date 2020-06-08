'''
Practica 3 - Redes 2
File: manage_users.py
Description: Archivo que se conecta 
con el servidor y envia las peticiones 
correspondientes a dicho servidor.
Authors:
    DanMat27
    AMP
'''
import sys
import os
import requests
import json
import socket

# URL del servidor
URL = 'vega.ii.uam.es'
# Puerto TCP del servidor
PORT_SERVER = 8000
# Puerto de conexion para control de llamadas
PORT_CONTROL = 2772
# Puerto de conexion para transmision de video
PORT_UDP = 1234
# Protocolo soportado
PROTOCOLO = 'V0'
# Nick del usuario actual
NICK_USUARIO = "aitor"


################################################################
# FUNCTION: def list_users_nicks()
#
# DESCRIPTION: Funcion que envia la peticion de listar
# usuarios registrados al servidor.
#
# ARGS_IN: None
#
# ARGS_OUT: respuesta - Lista de usuarios registrados.
################################################################
def list_users_nicks():
    # Creamos el socket TCP/IP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Nos conectamos con el servidor
        s.connect((URL, PORT_SERVER))
        # Creamos el mensaje a enviar
        message = 'LIST_USERS'
        # Enviamos el mensaje
        s.send(message.encode())
        # Recibimos la respuesta
        respuesta = s.recv(8192)
        return respuesta


################################################################
# FUNCTION: def register_user(nick,password)
#
# DESCRIPTION: Funcion que envia la peticion de registro
# al servidor de este usuario.
#
# ARGS_IN: nick - Nombre de usuario a registrar.
#          password - Contrasenia vinculada al nick.
#
# ARGS_OUT: respuesta - Mensaje de verificación o rechazo.
################################################################
def register_user(nick, password):
    # Creamos el socket TCP/IP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Nos conectamos con el servidor
        s.connect((URL, PORT_SERVER))
        # Creamos el mensaje a enviar
        # Conseguimos los datos del cliente
        ip = mi_ip()
        # Construimos el mensaje
        message = 'REGISTER ' + nick + ' ' + ip + ' ' + str(PORT_CONTROL) + ' ' + password + ' ' + PROTOCOLO
        # Enviamos el mensaje
        s.send(message.encode())
        # Recibimos la respuesta
        respuesta = s.recv(1024)
        return respuesta


################################################################
# FUNCTION: def query_user(nick)
#
# DESCRIPTION: Funcion que envia la peticion de consulta
# de información de un usuario en concreto.
#
# ARGS_IN: nick - Nick del usuario a buscar.
#
# ARGS_OUT: respuesta - Informacion del usuario.
################################################################
def query_user(nick):
    # Creamos el socket TCP/IP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Nos conectamos con el servidor
        s.connect((URL, PORT_SERVER))
        # Creamos el mensaje a enviar
        message = 'QUERY ' + nick
        # Enviamos el mensaje
        s.send(message.encode())
        # Recibimos la respuesta
        respuesta = None
        respuesta = s.recv(1024)
        return respuesta


################################################################
# FUNCTION: def quit_user()
#
# DESCRIPTION: Funcion que envia la peticion de cerrar la
# conexion creada por este usuario con el servidor.
#
# ARGS_IN: nick - Nick del usuario a buscar.
#
# ARGS_OUT: respuesta - Informacion del usuario.
################################################################
def quit_user():
    # Creamos el socket TCP/IP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Nos conectamos con el servidor
        s.connect((URL, PORT_SERVER))
        # Creamos el mensaje a enviar
        message = 'QUIT'
        # Enviamos el mensaje
        s.send(message.encode())
        # Recibimos la respuesta
        respuesta = s.recv(1024)
        return respuesta
    

################################################################
# FUNCTION: def mi_ip()
#
# DESCRIPTION: Funcion que devuelve la direccion IP del
# dispositivo actual y que se utilizará para la conexion
# de la llamada.
#
# ARGS_IN: None
#
# ARGS_OUT: ip - mi IP.
################################################################
def mi_ip():
    #Conectamos con una web cualquier (Google)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    #Obtenemos nuestra IP privada
    ip = s.getsockname()[0]
    print("\nMi IP es: " + ip)
    s.close()
    return ip


################################################################
# FUNCTION: def edit_users_list(users)
#
# DESCRIPTION: Funcion que devuelve la lista de usuarios 
# obtenida de LIST_USERS limpia y editada (String).
#
# ARGS_IN: users - Lista de usuarios.
#
# ARGS_OUT: newUsers - Nueva lista de usuarios.
################################################################
def edit_users_list(users):
    newUsers = ""
    users = users.decode("utf-8")
    #print(users)

    numUsers = users[14:16]
    i = 17
    if users[16] != ' ':
        numUsers = numUsers + users[16]
        i = 18
    numUsers = "Hay " + numUsers + " usuarios:\n"
    #print(numUsers)

    nick = True
    user = 1
    newUsers = newUsers + str(user) + "--->"
    while (i<len(users)):

        if users[i] == ' ':
            nick = False
        else:
            if nick == True:
                if users[i] != '#' and users[i] != ' ':
                    newUsers = newUsers + users[i]

        if users[i] == '#':
            user += 1
            newUsers = newUsers + "\n" + str(user) + "--->"
            nick = True

        i += 1

    return numUsers + newUsers


################################################################
# FUNCTION: def calling(user_nick)
#
# DESCRIPTION: Funcion que solicita una llamada a un usuario.
#
# ARGS_IN: user_nick - Nick del usuario a llamar.
#
# ARGS_OUT: respuesta - Respuesta del usuario.
################################################################
def calling(user_nick):
    # Consultamos los datos del usuario a llamar
    info = query_user(user_nick)
    # Sacamos la ip y puerto del usuario
    info = str(info)
    i = 16
    while info[i] != ' ':
        i = i + 1

    i = i + 1
    ip = ''
    while info[i] != ' ':
        ip += info[i]
        i+=1

    i = i + 1
    port = ''
    while info[i] != ' ':
        port += info[i]
        i+=1

    # Nos conectamos con el usuario
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Nos conectamos con el servidor
        s.connect((ip, int(port)))
        # Creamos el mensaje a enviar
        message = 'CALLING ' + NICK_USUARIO + ' ' + str(PORT_UDP)
        # Enviamos el mensaje
        s.send(message.encode())
        # Recibimos la respuesta
        respuesta = s.recv(1024)
        print('Respuesta recibida: ' + respuesta.decode())
        return ip, respuesta


################################################################
# FUNCTION: def end_call(user_nick)
#
# DESCRIPTION: Funcion que indica al otro usuario que se va a
# colgar la llamada en curso.
#
# ARGS_IN: user_nick - Nick del usuario en llamada.
#
# ARGS_OUT: None
################################################################
def end_call(user_nick):
    # Consultamos los datos del usuario a llamar
    info = query_user(user_nick)
    # Sacamos la ip y puerto del usuario
    info = str(info)
    i = 16
    while info[i] != ' ':
        i = i + 1

    i = i + 1
    ip = ''
    while info[i] != ' ':
        ip += info[i]
        i+=1

    i = i + 1
    port = ''
    while info[i] != ' ':
        port += info[i]
        i+=1

    # Nos conectamos con el usuario
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Nos conectamos con el servidor
        s.connect((ip, int(port)))
        # Creamos el mensaje a enviar
        message = 'CALL_END ' + NICK_USUARIO
        # Enviamos el mensaje
        s.send(message.encode())


################################################################
# FUNCTION: def accept_call(user_nick)
#
# DESCRIPTION: Funcion que comprueba si el cliente del usuario
# soporta nuestro mismo protocolo. Si no, se rechaza la llamada.
#
# ARGS_IN: user_nick - Nick del usuario que llama.
#
# ARGS_OUT: aceptar - True si se acepta, False si se rechaza.
################################################################
def accept_call(user_nick):
    # Consultamos los datos del usuario a llamar
    info = query_user(user_nick)
    # Sacamos los protocolos aceptados por el usuario
    info = info.decode()
    i = 14
    while info[i] != ' ':
        i += 1

    i = i + 1
    while info[i] != ' ':
        i += 1

    i = i + 1
    while info[i] != ' ':
        i += 1
    
    i = i + 1
    protocolo = ''
    aceptar = False
    while i < len(info):
        if info[i] == '#':
            if protocolo == PROTOCOLO:
                aceptar = True        
            print(protocolo)
            protocolo = ''
        else:
            protocolo += info[i]
        i += 1
    
    if protocolo == PROTOCOLO:
        aceptar = True
    
    return aceptar

