'''
Practica 3 - Redes 2
File: thread.py
Description: Archivo que almacena los
distintos hilos utilizados en la app
multimedia.
Authors:
    DanMat27
    AMP
'''
import threading
import ctypes
import time
import socket
import cv2
from datetime import *
from practica3_client import *

# Puerto de conexion para control de llamadas
PORT_CONTROL = 2772
# Puerto de conexion para transmision de video
PORT_UDP = 1234
# IP del dispositivo actual
IP = '192.168.1.110'
# Nick del usuario actual
NICK_USUARIO = "aitor"
# Tamanio del mensaje a enviar/recibir por UDP
BUFFER = 8192


################################################################
# CLASS: class wait_call_thread(threading.Thread)
#
# DESCRIPTION: Clase del hilo de espera de llamadas que hagan
# otros usuarios a nuestro cliente y controla las peticiones
# mediante TCP. 
# Esta puede aceptar una llamada (CALL_ACCEPTED), rechazarla
# por protocolo no soportado (CALL_DENIED) o rechazar por 
# usuario ocupado (CALL_BUSY).
# También se encarga de finalizar la llamada (CALL_END).
#
# ATRIBUTES:
#   name - Nombre del hilo.
#
# METHODS: 
#   def __init__(self, name) : Inicializa el hilo.
#   def run(self) : Funcion ejecutada por el hilo para la espera
#                   Puede aceptar una llamada, rechazarla por
#                   mala version o indicar que esta ocupado.
#                   Tambien se encarga de detener la llamada.
#   get_id(self) : Devuelve el ID del hilo.
#   raise_exception(self) : Lanza una excepcion del hilo.
#
################################################################
class wait_call_thread(threading.Thread):

    def __init__(self, name, w): 
        threading.Thread.__init__(self) 
        self.name = name
        self.w = w

    def run(self):
        global EN_LLAMADA, HILO2, HILO3
        print('Hilo de espera de llamadas activo...\n')
        # Abrimos el puerto de llamadas, el del server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((IP, PORT_CONTROL))
            s.listen(1)
            # Esperamos a recibir una llamada
            EN_LLAMADA = False
            while True: 
                conn, addr = s.accept()
                if conn:
                    solicitud = conn.recv(1024)
                    if solicitud != '':
                        if EN_LLAMADA == True:
                            if solicitud.decode()[:8] == "CALL_END":
                                # El receptor solicita finalizar la llamada
                                print("Llamada finalizada.\n")
                                respuesta = 'OK_CALL_END' + NICK_USUARIO
                                # Terminamos los hilos de envio y recepcion de frames 
                                HILO2.raise_exception() 
                                HILO2.join()
                                HILO3.raise_exception()
                                HILO3.join()
                            else:
                                # Usuario ya en llamada, se envia CALL_BUSY al llamante
                                print("Usuario ocupado.\n")
                                respuesta = 'CALL_BUSY ' + NICK_USUARIO
                            conn.send(respuesta.encode())

                        else:
                            # Usuario no en llamada, se podra aceptar la llamada
                            solicitud = solicitud.decode()
                            print('Llamada entrante: ' + solicitud)

                            # Sacamos el nick y el puerto del usuario que nos llama
                            i = 8
                            user_nick = ''
                            while solicitud[i] != ' ':
                                user_nick += solicitud[i]
                                i += 1

                            user_port = solicitud[i+1:]
                            #print("\nNICK/PUERTO: " + user_nick + "/" + user_port)

                            if accept_call(user_nick) == True:
                                # Llamada aceptada
                                respuesta = 'CALL_ACCEPTED ' + NICK_USUARIO + ' ' + str(PORT_UDP)
                                conn.send(respuesta.encode())

                                # Incluimos los nuevos botones de control de llamada
                                self.w.app.addButton("Pausar", self.w.buttonsCallback, 5, 0)
                                self.w.app.addButton("Colgar", self.w.buttonsCallback, 5, 2)

                                # Iniciamos el hilo UDP de la recepcion de frames
                                HILO2 = receive_video_call_thread('Receive Video Call Thread', self.w) 
                                HILO2.daemon = True
                                HILO2.start()

                                # Iniciamos el hilo UDP de envio de frames
                                HILO3 = send_video_call_thread('Send Video Call Thread', user_nick, user_port, self.w) 
                                HILO3.daemon = True
                                HILO3.start()

                                EN_LLAMADA = True

                            else:
                                # Llamada no cumple con nuestra version de protocolo soportada
                                respuesta = 'CALL_DENIED ' + NICK_USUARIO
                                conn.send(respuesta.encode())   


        
    def get_id(self): 
        if hasattr(self, '_thread_id'): 
            return self._thread_id 
        for id, thread in threading._active.items(): 
            if thread is self: 
                return id

    def raise_exception(self): 
        thread_id = self.get_id() 
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 
                ctypes.py_object(SystemExit)) 
        if res > 1: 
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0) 
            print('Exception raise failure\n') 


################################################################
# CLASS: class send_video_call_thread(threading.Thread)
#
# DESCRIPTION: Clase del hilo emisor que envia frames al usuario 
# receptor mediante UDP. El frame se captura de la webcam del 
# usuario y se muestra visualmente lo que se envia en la 
# interfaz. Luego, se envia el frame comprimido en formato JPG 
# con una cabecera con info util para control de flujo.
#
# ATRIBUTES:
#   name - Nombre del hilo.
#   receptor_port - Puerto UDP del usuario receptor.
#   receptor_ip - IP del usuario receptor.
#   w - Objeto de la clase VideoClient.
#
# METHODS: 
#   def __init__(self, name) : Inicializa el hilo.
#   def run(self) : Funcion ejecutada por el hilo para el envio
#                   de los datagramas UDP con los frames.
#   get_id(self) : Devuelve el ID del hilo.
#   raise_exception(self) : Lanza una excepcion del hilo.
#
################################################################
class send_video_call_thread(threading.Thread):

    def __init__(self, name, receptor_port, receptor_ip, w): 
        threading.Thread.__init__(self) 
        self.name = name
        self.receptor_ip = receptor_ip
        self.receptor_port = receptor_port
        self.w = w


    def run(self):
        print('Hilo UDP de envio en la videollamada activo...\n')

        #Capturamos la camara 
        self.w.cap = cv2.VideoCapture(0)
        self.w.app.setPollTime(20)

        # Creamos el socket TCP/IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Vamos enviando frame a frame el video
            i = 1
            while True:
                frame = None
                header = None
                data = b''
                # Capturamos un frame de la cámara o del vídeo
                ret, frame = self.w.cap.read()
                frame = cv2.resize(frame, (640, 480))
                cv2_im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img_tk = ImageTk.PhotoImage(Image.fromarray(cv2_im))

                # Lo mostramos en el GUI
                self.w.app.setImageData("mi_video", img_tk, fmt='PhotoImage')

                # Se envia el frame a la red 
                encode_param = [cv2.IMWRITE_JPEG_QUALITY,50]
                result,encimg = cv2.imencode('.jpg',frame,encode_param)
                if result == False: 
                    print('Error al codificar imagen')
                encimg = encimg.tobytes()
                # Se crea su cabecera y se envia junto al frame comprimido
                header = (str(i) + '#' + str(datetime.now()) + '#' + '640x480' + '#' + '20' + '#').encode()   
                data = header + encimg
                s.sendto(data, (self.receptor_ip, int(self.receptor_port)))
                i += 1

        
    def get_id(self): 
        if hasattr(self, '_thread_id'): 
            return self._thread_id 
        for id, thread in threading._active.items(): 
            if thread is self: 
                return id
    
    def raise_exception(self): 
        thread_id = self.get_id() 
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 
                ctypes.py_object(SystemExit)) 
        if res > 1: 
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0) 
            print('Exception raise failure\n') 


################################################################
# CLASS: class receive_video_call_thread(threading.Thread)
#
# DESCRIPTION: Clase del hilo receptor que recibe los frames del
# otro usuario emisor mediante UDP. El frame se descomprime y se
# muestra visualmente en la interfaz. La cabecera no se utiliza
# en esta versión.
#
# ATRIBUTES:
#   name - Nombre del hilo.
#   w - Objeto de la clase VideoClient.
#
# METHODS: 
#   def __init__(self, name) : Inicializa el hilo.
#   def run(self) : Funcion ejecutada por el hilo para recibir
#                   los datagramas UDP con los frames.
#   get_id(self) : Devuelve el ID del hilo.
#   raise_exception(self) : Lanza una excepcion del hilo.
#
################################################################
class receive_video_call_thread(threading.Thread):

    def __init__(self, name, w): 
        threading.Thread.__init__(self) 
        self.name = name
        self.w = w


    def run(self):
        print('Hilo UDP de recepcion en la videollamada activo...\n')
        # Creamos el socket TCP/IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Iniciamos el servidor de recepcion
            s.bind((IP, PORT_UDP))

            while True:             
                data = b'' 
                # Obtenemos los mensajes con los frames
                while True:
                    data = s.recv(BUFFER)
                    if data:
                        # Separamos la cabecera del frame por el separador '#'
                        data_split = data.split(b'#',4)
                        #print(data_split)

                        # Extraemos el frame y lo editamos
                        frame = cv2.imdecode(np.frombuffer(data_split[4],np.uint8), 1)
                        frame = cv2.resize(frame, (640, 480))
                        cv2_im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        img_tk = ImageTk.PhotoImage(Image.fromarray(cv2_im))

                        # Lo mostramos en el GUI
                        self.w.app.setImageData("video_receptor", img_tk, fmt='PhotoImage')

        
    def get_id(self): 
        if hasattr(self, '_thread_id'): 
            return self._thread_id 
        for id, thread in threading._active.items(): 
            if thread is self: 
                return id

    def raise_exception(self): 
        thread_id = self.get_id() 
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 
                ctypes.py_object(SystemExit)) 
        if res > 1: 
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0) 
            print('Exception raise failure\n') 
