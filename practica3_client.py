'''
Practica 3 - Redes 2
File: practica3_client.py
Description: Archivo principal
que inicia la aplicacion multimedia,
iniciando su interfaz y permitiendo
al usuario obtener info del servidor
y llamar a otros usuarios.
Authors:
    DanMat27
    AMP
'''
# import the library
from appJar import gui
from PIL import Image, ImageTk
import numpy as np
import cv2
import socket
from manage_users import *
from thread import *

# Macros con info del usuario actual
NICK_USUARIO = "aitor"
PWD_USUARIO = "password"


################################################################
# CLASS: class VideoClient(object)
#
# DESCRIPTION: Clase de la ventana principal que se configura 
# nada mas iniciar la aplicacion. Contiene distintas opciones 
# para el usuario, ejecutando llamadas al servidor y permite 
# crear una llamada con otro usuario distinto.
#
# ATRIBUTES:
#   app - Objeto de la gui
#   nick_receptor - Nick del receptor si hay llamada
#
# METHODS: 
#   def __init__(self, window_size) : Inicializa la ventana
#
#   def start(self) : Inicia y muestra la ventana
#
#   buttonsCallback(self, button) : Contiene las funciones 
#   ejecutadas por cada uno de los eventos de los botones
#   que posee la ventana. Las opciones son: Salir de la app, 
#   Registrarse en el servidor, Listar los usuarios registrados 
#   en el servidor, Consultar la informacion de un usuario,
#   Realizar una llamada a otro usuario, Colgar la llamada,
#   Pausar la llamada actual y Reanudar la llamada pausada.
#
################################################################
class VideoClient(object):

    def __init__(self, window_size):
        global HILO

        self.nick_receptor = None

        #Creamos la interfaz
        self.app = gui("Redes2 - P2P", window_size)
        self.app.setGuiPadding(20, 20)
        self.app.setSize(1000, 800)
        #Color de la interfaz
        self.app.setBg("lightblue")

        #Titulo 
        self.app.addLabel("title", "Cliente Multimedia P2P - Redes2 ", 0, 1)

        #Video
        self.app.addLabel("user", NICK_USUARIO, 1, 0)
        self.app.addImage("mi_video", "imgs/webcam.gif", 2, 0)
        self.app.addLabel("receptor", "Receptor", 1, 2)
        self.app.addImage("video_receptor", "imgs/webcam.gif", 2, 2)

        #Botones de la ventana
        self.app.addButton("Registrarse", self.buttonsCallback, 3, 0)
        self.app.addButton("Listar usuarios", self.buttonsCallback, 3, 2)
        self.app.addButton("Consultar informacion", self.buttonsCallback, 4, 0)
        self.app.addButton("Iniciar llamada", self.buttonsCallback, 4, 2)
        self.app.addButton("Salir", self.buttonsCallback, 6, 1)
        #Colores de los botones
        self.app.setButtonBg("Registrarse", "White")
        self.app.setButtonBg("Listar usuarios", "White")
        self.app.setButtonBg("Consultar informacion", "White")
        self.app.setButtonBg("Iniciar llamada", "White")
        self.app.setButtonBg("Salir", "White")

        #Se crea el hilo de espera de llamadas entrantes
        HILO = wait_call_thread('Waiting Calls Thread', self) 
        HILO.daemon = True
        HILO.start()

    def start(self):
        self.app.go()

    def buttonsCallback(self, button):

        if button == "Salir":
            # Cerramos conexion con el server y salimos de la aplicación
            salida = quit_user()
            self.app.infoBox("Cerrando conexion...", salida)
            print("Cerrada conexion del usuario: " + NICK_USUARIO)
            self.app.stop()

        elif button == "Registrarse":
            # Registramos nick de usuario
            nick = self.app.textBox(
                "Registro", "Introduce tu nick de usuario:")
            pwd = self.app.textBox(
                "Registro", "Introduce tu contraseña de usuario:")
            if nick:
                respuesta = register_user(nick, pwd)
                self.app.infoBox("Registro", respuesta)
            
        elif button == "Listar usuarios":
            # Listamos usuarios de la aplicacion
            users = list_users_nicks()
            if users:
                users = edit_users_list(users)
                self.app.infoBox("Usuarios registrados", users)

        elif button == "Consultar informacion":
            # Mostramos la informacion de los usuarios
            nick = self.app.textBox("Info", "Introduce el nick del usuario:")
            if nick:
                user_data = query_user(nick)
                self.app.infoBox("Informacion de usuario", user_data)

        elif button == "Iniciar llamada":
            global HILO2, HILO3

            # Cambiamos a otra ventana donde se inicia una llamada de video
            user_nick = self.app.textBox("Iniciar llamada", "Introduce el nick del usuario:")
            ip,respuesta = calling(user_nick)
            # Sacamos la informacion del usuario, si acepta la llamada
            aux = respuesta
            verificacion_call = aux[:9]
            verificacion_call.decode('utf-8')
            respuesta = str(respuesta)
            if verificacion_call == 'CALL_BUSY'.encode():
                print("La llamada ha sido rechazada porque el receptor esta ocupado\n")
            else:
                print("La llamada ha sido rechazada por no poseer el mismo protocolo que el receptor\n")
            
            verificacion_call = aux[0:13]
            verificacion_call.decode('utf-8')
            respuesta = str(aux)
            if verificacion_call == 'CALL_ACCEPTED'.encode():
                i = 16
                receptor_nick = ''
                while respuesta[i] != ' ':
                    receptor_nick += respuesta[i]
                    i = i + 1

                receptor_port = respuesta[i:-1]

                # Incluimos los nuevos botones de control de llamada
                self.app.addButton("Pausar", self.buttonsCallback, 5, 0)
                self.app.addButton("Colgar", self.buttonsCallback, 5, 2)

                # Iniciamos el hilo UDP de la recepcion de frames
                HILO2 = receive_video_call_thread('Receive Video Call Thread', self) 
                HILO2.daemon = True
                HILO2.start()

                # Iniciamos el hilo UDP de envio de frames
                HILO3 = send_video_call_thread('Send Video Call Thread', receptor_port, ip, self) 
                HILO3.daemon = True
                HILO3.start()

                self.nick_receptor = receptor_nick

        elif button == "Colgar":
            if self.nick_receptor:
                end_call(self.nick_receptor)
                print("Llamada finalizada.\n")
                # Cerramos el cliente
                self.app.stop()

        elif button == "Pausar":
            # Se pausa la video llamada
            # No implementado
            self.app.addButton("Reanudar", self.buttonsCallback, 5, 1)
        
        elif button == "Reanudar":
            # Se reanuda una llamada pausada
            # No implementado
            self.app.stop()



if __name__ == '__main__':

    #Registramos al usuario de este cliente al entrar
    respuesta = register_user(NICK_USUARIO, PWD_USUARIO)

    # Si el usuario ha iniciado sesion bien, se pone en espera de llamada en paralelo
    verificacion = respuesta[0:2]
    verificacion.decode('utf-8')
    if verificacion == 'OK'.encode():
        print("Registrada conexion del usuario: " + NICK_USUARIO)

        #Iniciamos la ventana inicial
        wc = VideoClient("640x520")
        wc.start()

    else:
        #En caso de error en el registro
        print("Fallo en el registro del usuario: " + NICK_USUARIO)


