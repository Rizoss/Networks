#!/usr/bin/pyhton3
#-*- coding: utf-8; mode python -*-

############################################ Librerias ##############################################
import socket
import hashlib
import base64
import struct
import urllib.request, urllib.parse, threading
import os
import signal
import time 

############################################# GYMKANA ###############################################

############################################# PASO 0 ################################################

# En el paso(reto) 0, tenía que crear un cliente y conectarme al servidor, una vez
# conseguido, enviar mi nombre de usuario al servidor.


def paso0():

    sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockTCP.connect(('node1',2000))
    msg1 = sockTCP.recv(1024).decode()
    print(msg1)
    nombre="beatriz.munoz16".encode()
    sockTCP.send(nombre)
    msg2 = sockTCP.recv(1024)
    print(msg2.decode())
    sockTCP.close() #funciona hasta aqui

    return msg2.decode()[0:36]

############################################# PASO 1 ###############################################

# En el paso 1 debía crear un servidor udp, definir mi propio puerto y enviar el código del anterior reto


def paso1(id1):
    
    sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    code = str(1985)+" "+id1
    sockUDP.bind(('',1985))
    sockUDP.sendto(code.encode(), (('node1', 3000)))
    msg, data= sockUDP.recvfrom(2048)
    print(msg.decode())
    sockUDP.close()

    return msg.decode()[5:41]

############################################# PASO 2 ###############################################

# En el paso 2 tenía que conectarme al servidor TCP, para ello creo un socket SOCK_STREAM
# defino un par de variables que me serán de gran utilidad. En un bucle "infinito" voy recibiendo los datos
# que me envía el servidor. En el caso de que encuentre un 0, saldré del bucle, si por el contrario no encuentro el 0
# iré recibiendo más datos y los iré concatenando.

# Llamaré a la función number_counter para poder obtener los numeros que hay antes del 0, recibiré un encuentro
# que enviaré junto al código del anterior reto al servidor. 

# Por último creo un bucle "infinito" que irá recogiendo la 'basura', en el caso de que encuentre 'code:' en los datos
# recibidos saldŕa del bucle y lo imprimirá por pantalla.


def paso2(id2):
    
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect(('node1', 4001))
    number = ''
    msg = ''
    while 1:
        number += cliente.recv(4096).decode()
        if ' 0 ' in number:
            break

    contador = number_counter(number)
    envio = id2+" "+str(contador)
    cliente.send(envio.encode())
    while 1:
        msg = cliente.recv(1024).decode()
        if 'code:' in msg or 'Wrong answer:' in msg:
            print(msg)
            break

    cliente.close()

    return msg[5:41]

########################################## FUNCIONES PASO 2 ######################################   

# Esta función se utiliza en el paso 2 para poder contar los numeros que hay en el mensaje antes de encontrar el 0.

    
def number_counter(number):
    contador = 0
    mensaje = number.split()
    for i in mensaje:
        if i == '0':
            return contador
            break
        else:
            contador += 1

############################################# PASO 3 ###############################################

# En este paso (paso 3 , como en el paso anterior debo conectarme a un servidor TCP) crearé un bucle "infinito" donde iré recibiendo los datos que me proporciona el servidor. Cada mensaje lo analizo en busca de un palindromo,
# en el caso de que no haya encontrado el palindromo sigo recibiendo datos y concatenandolos.
# En el caso de que encuentre el palindromo salgo del bucle, al haber obtenido los datos y el palindromo
# llamaré a la función obtener_mensaje que me proporcionará el mensaje al revés. Una vez obtenido
# dicho mensaje lo enviaré al servidor, y a continuación enviaré el código de mi reto anterior.

# Por último como en paso anterior creo un bucle para capturar los residuos, en el caso de que encuentre 'code:' o 'Wrong answer'
# saldŕa del bucle y lo imprimirá por pantalla.

def paso3(id3):

    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect(('node1',6000))
    datos = ''
    msg = ''
    while 1: 
        datos += cliente.recv(1024).decode()
        palindromo = tratar(datos)
        if palindromo != '':
            break
    
    message = obtener_mensaje(datos, palindromo)
    code = "--"+id3+"--"
    cliente.send(message.encode())
    cliente.send(code.encode())
    while 1:
        msg = cliente.recv(1024).decode()
        if 'code:' in msg or 'Wrong answer:' in msg:
            break

    print(msg)
    cliente.close()
    return msg[5:41]

####################################### FUNCIONES PASO 3 ###############################################

# obtener_mensaje se encarga de darle la vuelta al mensaje, mientras no sea un número. 
# Para realizar esto utilizo una lista auxiliar aux[]. 

def obtener_mensaje(datos, palindromo):
    aux = []
    new = datos.split(" ")
    for word in new:
        if (word.isdigit() == False):
            if word != palindromo:
                reverse = invertir_palabra(word)
                aux += [reverse]
            else:
                aux += [palindromo]
        else:
            aux += [word]

    cadena_enviar = ' '.join(aux)
    enviar = cadena_enviar.split(palindromo)
    mensaje = enviar[0]
    return mensaje[:-1]

# tratar se encargaŕa de comprobar si hay algún palindormo en los datos obtenidos hasta el momento, en el caso de que encuentre
# el palindromo se lo devolverá al paso 3 para poder seguir con la ejecución del paso.

def tratar(datos):
    palindromo = ''
    cadena = datos.split()
    for word in cadena:
        if not word.isdigit() and len(word) > 1:
            booleano = True
            if (word != word[::-1]):
                booleano = False
            if booleano:
                palindromo = word
                break

    return palindromo
    
# es_palindromo comprobará si las palabras que se encuentran en los datos recibidos, en el caso
# de que sea palindromo devolverá verdadero, por el contrario devolverá falso.

def es_palindromo(word):
    palabra = word.lower()
    if palabra == palabra[::-1]:
        return True
    else:
        return False
    
# invertir_palabra se encargará de darle la vuelta a las palabras
 
def invertir_palabra(word):
    return word[::-1]
    
############################################# PASO 4 ###############################################

# Este paso consiste en conectarse al servidor, enviarle el código del paso anterior y recibir un primer mensaje
# que contiene el tamaño del archivo (fichero) antes de los : , y después creo un bucle condicional, que recibirá datos mientras 
# el tamaño de los bytes recibidos (datos) sea menor que el tamaño del fichero.

# Después utilizo la libreria hashlib para poder usar el md5 y poder calcular md5 sum, después envío el resultado al servidor.
# Como anteriormente hice utilizo un bucle para los datos residuales.

def paso4(id4):
    
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect(('node1',10000))
    cliente.send(id4.encode())
    msg = cliente.recv(24)
    reto = ''
    mensaje = msg.split(b':')
    size_bytes = int(mensaje[0].decode())
    msg_completo = mensaje[1]
    bytes_recv = len(mensaje[1])
    while bytes_recv < size_bytes:
        message = cliente.recv(1024)
        bytes_recv += len(message)
        msg_completo += message
    
    md5 = hashlib.md5()
    md5.update(msg_completo)
    cliente.sendall(md5.digest())
    while 1:
        reto = cliente.recv(1024).decode()
        if 'code:' in reto or 'Wrong answer' in reto:
            break
    print(reto)
    return reto[5:41]
    
############################################# PASO 5 ###############################################

# El paso 5 consiste en enviar tu código anterior codificado en base64. 
# Enviaremos una solicitud (request) WYP, para ello utilizaremos las funciones para empaquetar 
# los paquetes. 
# - Message format:
#   +---------+----------------------------+
#   | header  |  payload                   |
#   +---------+----------------------------+
# - Header format:
#   +-------+------+------+----------+
#   | "WYP" | type | code | checksum |
#   +-------+------+------+----------+
#      3       1      2        2        (bytes)

#   where:
#   - type: 0:request, 1:reply
#   - code: 0:no-error, 1:wrong-code, 2:wrong-format,
#           3:wrong-challenge, 4:wrong-checksum
#     - 'code' must be 0 on requests
#   - checksum: Internet checksum (RFC1071) for the whole message
#   - payload:
#     - Text encoded with base64 format

# En este paso haré uso de los métodos proporcionados por el profesor David Villa Alises

def paso5(id5):

    sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    payload = base64.b64encode(id5.encode()) #carga util, codificamos con base64 nuesto identificador.
    nombreProtocolo = 'WYP'.encode() #codificamos nuestro nombre del protocolo
    size_type = (0).to_bytes(2,"big") #conversion de un int en bytes big-endian
    size_code = (0).to_bytes(1,"big")
    type = struct.unpack("H",size_type) #tipo
    code = struct.unpack("B",size_code)
    wyp = struct.pack('!3sHB',nombreProtocolo,type[0],code[0])+payload
    checksum = cksum(wyp) #calcula el checksum con los métodos proporcionados
    checksumBy = checksum.to_bytes(2,"big")
    wyp = struct.pack('!3sHBH',nombreProtocolo,type[0],code[0],checksum)+payload
    sockUDP.sendto(wyp,('node1',7001))
    mensaje, nodo = sockUDP.recvfrom(4098)
    reto = mensaje[8:]
    print(base64.b64decode(reto).decode())
    reto_decodificado = base64.b64decode(reto).decode()
    reto_decodificado_div = reto_decodificado.split('Challenge 6:')
    codigo = reto_decodificado_div[0].split('code:')
    id_6 = codigo[1].split("\n")
    return id_6[0]
    
#Copyrigth (C) David Villa Alises
def sum16(data):
    if len(data) % 2:
        data = b'\0' + data

    return sum(struct.unpack('!%sH' % (len(data) // 2), data))

#Copyrigth (C) David Villa Alises
def cksum(data):
    sum_as_16b_words  = sum16(data)
    sum_1s_complement = sum16(struct.pack('!L', sum_as_16b_words))
    _1s_complement    = ~sum_1s_complement & 0xffff
    return _1s_complement

############################################# PASO 6 ###############################################

# Este paso consiste en la creación de un WEB SERVER POST, para ello utilizaré los hilos (threads), para crear subprocesos.
# Lo primero que haré seŕa conectarme al servidor TCP, por lo que creo un socket_cliente al que le enviaŕe el el código del paso
# anterior junto con  el puerto que utilizaré.

# Creo un sock_server, junto con listen para poder escuchar las peticiones de los clientes conectados a mi puerto (el antes mencionado).
# Para poder atender a los clientes, crearé varios hilos que harán las peticiones HTTP.

def paso6(id6) :
    sock_client= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Estableciendo la conexión...")
    sock_client.connect(('node1',8003))
    print("La conexión se ha establecido.")
    mi_puerto = 8363
    message = id6.encode()+b' '+str(mi_puerto).encode()
    sock_client.send(message)
    sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_server.bind(('', mi_puerto))
    print("Puerto de escucha. " + str(mi_puerto) + ". Esperando clientes...")
    sock_server.listen(30)
    threading.Thread(target=hilo, args=(sock_server,)).start()
    sock_client.close() # Cierre del Cliente

############################################# FUNCIONES PASO 6 ###############################################

# hilo: esta funcion crea un bucle infinito donde se aceptarán las peticiones de los clientes conectados a mi servidor,
# y a su vez creará mas hilos que harán peticiones http a mi servidor.


def hilo(sock_server):
    while True:
        sockCliente, address = sock_server.accept()
        time.sleep(0.2)
        threading.Thread(target = peticion_http, args = (sockCliente,sock_server)).start()


# peticion_http_ esta función recibirá las peticiones de los clientes conectados a mi servidor, en el caso de que el mensaje
# contenga 'code:' imprimiremos la etición y llamaré al siguiente paso (paso 7)

# En el caso de que en las peticiones se encuentre '/rfc' y no de error en las búsqueda
# intentaremos leer la url que se nos proporcionaba en el enunciado junto con la extensión de la petición.
# Para obtener la extensión haré un split(), para poder obtener el rfc de la petición.

# Una vez leida la url, concatenaremos el mensaje de OK porporcionado en el enunciado junto con la extensión
# antes mencionada, después se enviaŕa ese mensaje y para que el usuario se entere de que pasa, se mostrara el mensaje por la pantalla.

# En el caso de que haya un error se enviará el mensaje Not Found y se mostrará por pantalla, después se cerrará ese cliente. (desconexión)


def peticion_http(sockCliente, sock_server):
    peticion_http = sockCliente.recv(1024).decode()
    if 'code:' in peticion_http:
        print(peticion_http)
        paso7(peticion_http)
        sock_server.close()

    rfc_ = peticion_http.split()
    req_extension = rfc_[1]

    if req_extension.find('/rfc') != -1:
        try:
            url = urllib.request.urlopen("https://uclm-arco.github.io/ietf-clone/rfc"+req_extension+"")
            fichero = url.read()
            header = "HTTP/1.1 200 OK\n"+req_extension
            reply = header.encode()+fichero
            print("Peticion: "+req_extension+": 200 [OK]")
            url.close()
        except err_url as e:
            print("Peticion: "+req_extension+": 404 [NOT FOUND]")
            reply = "HTTP/1.1 404 Not Found\n"+req_extension
        sockCliente.send(reply)
        sockCliente.close()

############################################# PASO 7 ###############################################

# Paso 7 y ultimo de la gymkana, este paso es parecido al paso 0.
# Enviaremos al servidor TCP el código del reto y recibiremos el mensaje de respuesta: Congratulations! You PASSED all challenges!


def paso7(enunciado):
    msg = enunciado.split('code:')
    parteMsg = msg[1].split('\n')
    code = parteMsg[0]
    print("codigo reto")
    print(code)
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect(('node1',33333))
    cliente.send(code.encode())
    msg_recv = cliente.recv(1024).decode()
    print(msg_recv)
    cliente.close()  

############################################# MAIN ###############################################

# funcion main encargada de llamar a todos los pasos.

def main():
    id1 = paso0()
    id2 = paso1(id1)
    id3 = paso2(id2)
    id4 = paso3(id3)
    id5 = paso4(id4)
    id6 = paso5(id5)
    paso6(id6)

main()

##################################### ENLACES DE CONSULTA ########################################

# A continuación los enlaces que he utilizado para consultar cosas para los pasos anteriores.

# https://python-para-impacientes.blogspot.com/2016/12/threading-programacion-con-hilos-i.html

# https://docs.python.org/3/library/stdtypes.html#int.to_bytes

# https://stackoverflow.com/questions/19071512/socket-error-errno-48-address-already-in-use

# https://rico-schmidt.name/pymotw-3/array/index.html

# https://rico-schmidt.name/pymotw-3/struct/

# https://es.stackoverflow.com/questions/341450/pal%c3%adndromo-con-may%c3%basculas-sin-modificar-palabra

# https://es.stackoverflow.com/questions/194809/como-invertir-palabras-individuales-de-un-string-con-python/194811
