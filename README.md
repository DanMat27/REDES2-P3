# practica3

Práctica 3

Para probar esta práctica no es necesario realizar ningún compilado previo, ya que se realiza
sobre Python3.

El usuario puede probar la funcionalidad de este cliente multimedia con el siguiente comando:
> python3 practica3_client.py

Este cliente, nada más acceder, registra al usuario cuyo nombre y contraseña se encuentran en
las variables NICK_USUARIO y PWD_USUARIO. Si se quisiera cambiar esta información, habría 
que modificar estas variables en todos los módulos donde se encuentren declaradas.
En cuanto a los puertos UDP y la IP, se encuentran en las variable PORT_UDP para la conexion
UDP del envio de frames, en PORT_CONTROL para la conexión TCP de control de las llamadas y en
IP correspondiente a nuestra ip pública (al registrarse se envia la IP privada y esta es la 
que tenemos por defecto, ya que se ha probado solo localmente con dos clientes con puertos
distintos).

Una vez iniciada la interfaz, el usuario tiene varias opciones:
1. Registrarse de nuevo en el servidor con nuevo nick y contraseña. Aunque si ya se ha
registrado nada más iniciar la app esto es innecesario.
2. Listar todos los usuarios registrados en el servidor. Se muestra un pop-up con la lista.
3. Buscar información (IP, Puerto y Protocolos) de un usuario existente en el servidor.
4. Iniciar una llamada con un usuario activo en el servidor. Esto se debe realizar de forma
manual, introduciendo el nick del usuario a realizar la petición de llamada. 
5. Una vez iniciada la llamada, se puede pausar. (No implementado)
6. Una vez pausada la llamada, se puede reanudar por donde se había detenido. (No implementado)
7. Una vez iniciada la llamada, se puede colgar y terminar la llamada.
8. Salir de la aplicación.

La interfaz muestra dos pantallas, a la izquierda es la grabación de nuestra webcam y la de 
la derecha es la grabación de la webcam de la otra persona con la que contactamos.

Para que este cliente funcione correctamente, es necesario que exista la carpeta imgs/ en la
raíz del proyecto y dentro el archivo webcam.gif, con el que se grabará la cámara.

El servidor utilizado para este cliente multimedia es: https://vega.ii.uam.es:8000

Para más información detallada de la práctica, leerse la wiki del repositorio.
