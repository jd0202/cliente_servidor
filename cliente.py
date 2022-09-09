import zmq
import math
import os
from hash import md5Hash
import json

'''
0: Archivo recibido
1: Ya existe el archivo
2: Ya existe un archivo con ese mismo nombre
3: Su usuario no cuenta con el archivo que quiere descargar
'''

context = zmq.Context()

#  Socket to talk to server
print("Connecting to server...")
socket = context.socket(zmq.REQ)
ip_proxy="tcp://"+input("ingrese la direccion del servidor proxy: ")
puerto = input("ingrese el puerto del proxy: ")
proxy=ip_proxy+":"+puerto
socket.connect(proxy) #se conecta al proxy
#socket.connect("tcp://localhost:5555") #se conecta al proxy

name_client=input("Identificate, Nombre: ") # se solicita el nombre del cliente

print("Que operacion desea realizar")
print("1. Subir un archivo")
print("2. Descargar un archivo")
op=input("Operacion: ")
if op == "1":
    name_file=input("Nombre de archivo a enviar: ") #se solicita el nombre del archivo a enviar

    '''
    struct message:
    upload
        [id(cx),u,name_client,name_file,hash,num_all_parts...]
    '''
    size=1024*1024*1024 #se calcula el espacio a leer con cada parte

    if os.path.exists(name_file): # se valida si existe el archivo
        print("Enviando archivo") 
        size_file = os.path.getsize(name_file) #se obtiene el espacio que ocupa el archivo
        print("Tamaño de archivo: "+str(size_file)+" bytes")

        dm5_hash = md5Hash(name_file) #se obtiene el hash del archivo
        num_all_parts = math.ceil(size_file/size) #se calcula el numeor de partes en las que se dividira el archivo
        print("Partes a enviar: "+str(num_all_parts))

        # se envia al proxy el nombre del cliente, el nombre del archivo, el hash del archivo y el numero de partes en los que se dividira el archivo
        socket.send_multipart([b'cx', b'u', bytes(name_client.encode()), bytes(name_file.encode()), bytes(dm5_hash.encode()), bytes(str(num_all_parts).encode())]) 
        message = socket.recv_multipart() #se recibe el mensaje por parte del proxy
        if message[0].decode() == "0": #respuesta para codigo 0
            print(f"Received reply result: Archivo recibido") 
        elif message[0].decode() == "1" : #respuesta para codigo 1
            print(f"Received reply result: Ya cuenta cuenta con ese archivo")
        elif message[0].decode() == "2" : #respuesta para codigo 2
            print(f"Received reply result: Ya cuenta con un archivo con ese nombre")
        else:
            count_part=1 #contador de partes de archivo
            limit=0 #variable para controlar el limite de partes que iran a cada servidor
            #############################
            with open (name_file,"rb") as f: #se abre el archivo a enviar
                #contenido = f.read(size)
                #socket.disconnect("tcp://localhost:5555")# se desconecta del proxy
                socket.disconnect(proxy)# se desconecta del proxy
                for i in message: #se recorre el mensaje del proxy
                    addr=i.decode().split('-') #se separa la cadena para tener la direccion del servidor y la cantidad de partes que van en el
                    print(addr[0])
                    socket.connect(addr[0]) #Se conecta al servidor en cuestion para enviar las aprtes que le corresponden
                    limit+=int(addr[1]) #se establece el limite de partes
                    while count_part <= limit: #se valida que nos e envien mas partes de las designadas al cliente
                        contenido=f.read(size) #se lee un parte del archivo
                        #print(bytes((dm5_hash+"_"+str(count_part)).encode()))
                        socket.send_multipart([b'u',bytes((dm5_hash+"_"+str(count_part)).encode()), contenido]) #se envia al servidor la informacion leida
                        message = socket.recv() #se recibe la respeusat del server
                        count_part+=1 # se incrementa el contador de aprtes
                    socket.disconnect(addr[0]) #se desconecta del servidor para conetarse al siguiente
                f.close() #se cierra el archivo una vez leido
    else:
        print("Archivo no encontrado, por favor revise el nombre del archivo")
elif op == "2":
    name_file=input("Nombre de archivo a descargar: ") #se solicita el nombre del archivo a descargar
    '''
    struct message:
    dowload
        [id(cx),d,name_client,name_file...]
    '''
    # se envia al proxy el nombre del cliente y el nombre del archivo a descargar
    socket.send_multipart([b'cx', b'd', bytes(name_client.encode()), bytes(name_file.encode())]) 
    message = socket.recv_multipart() #se recibe el mensaje por parte del proxy
    if message[0].decode() == "3": #respuesta para codigo 3
        print(f"Received reply result: Su usuario no cuenta con el archivo que quiere descargar") 
    else:
        count_part=1 #contador de partes de archivo
        limit=0 #variable para controlar el limite de partes que iran a cada servidor
        dm5_hash = message[-1].decode()
        print(type(dm5_hash))
        print(dm5_hash)
        print(message)
        socket.disconnect(proxy)# se desconecta del proxy
        
        for i in message[:-1]: #se recorre el mensaje del proxy
            addr=i.decode().split('-') #se separa la cadena para tener la direccion del servidor y la cantidad de partes que van en el
            print(addr[0])
            socket.connect(addr[0]) #Se conecta al servidor en cuestion para enviar las aprtes que le corresponden
            limit+=int(addr[1]) #se establece el limite de partes
            if not(os.path.exists("Descargas")):
                os.mkdir("Descargas")
            while count_part <= limit: #se valida que nos e envien mas partes de las designadas al cliente
                f=open("Descargas/"+name_file,"ab")
                socket.send_multipart([b'd',bytes((dm5_hash+"_"+str(count_part)).encode())])
                message = socket.recv_multipart()
                f.write(message[0])
                f.close()
                count_part+=1
            socket.disconnect(addr[0])
        print("Archivo descargado")





