import zmq
import math
import os
import json
from functions import *

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
ip_server="tcp://"+input("ingrese la direccion del servidor: ")
puerto = input("ingrese el puerto del proxy: ")
server=ip_server+":"+puerto
socket.connect(server) #se conecta al servidor
filecJson = "filesc.json"

if not(os.path.exists(filecJson)):
    save_file_info(dict(), filecJson)

with open(filecJson) as files:
    data_files = json.load(files)

print("Que operacion desea realizar")
print("1. Subir un archivo")
print("2. Descargar un archivo")
op=input("Operacion: ")
if op == "1":
    name_file=input("Nombre de archivo a enviar: ") #se solicita el nombre del archivo a enviar

    '''
    struct message:
    upload
        [b'cu', name, file]
    archivo no en el dominio
        [b'cd', b'ND', predecesor(ip:port)]
    '''
    #size=1024*1024*1024 #se calcula el espacio a leer con cada parte
    size=1024*1024*10 #se calcula el espacio a leer con cada parte

    if os.path.exists(name_file): # se valida si existe el archivo
        if name_file in data_files.keys():
            print("Ya cuenta ha enviado una archivo con el mismo nombre")
        else:
            print("Enviando archivo") 
            size_file = os.path.getsize(name_file) #se obtiene el espacio que ocupa el archivo

            sha1_hash = sha1Hash(name_file) #se obtiene el hash del archivo
            num_all_parts = math.ceil(size_file/size) #se calcula el numeor de partes en las que se dividira el archivo
            print("Partes a enviar: "+str(num_all_parts))
            data_files[name_file] =  []#se crea el nuevo hash

            with open (name_file,"rb") as f:
                contenido=f.read(size) #se lee un parte del archivo
                sha1_hash = hashlib.sha1(contenido).hexdigest()
                socket.send_multipart([b'cu', bytes(sha1_hash.encode()), contenido])
                message = socket.recv_multipart()
                while message[1].decode() == "ND":
                    socket.disconnect(server)
                    server = message[2].decode()
                    socket.connect(server)
                    socket.send_multipart([b'cu', bytes(sha1_hash.encode()), contenido])
                    message = socket.recv_multipart()
                data_files[name_file].append(sha1_hash)
                save_file_info(data_files,filecJson)
            print("Archivo enviado")
    else:
        print("Archivo no encontrado, por favor revise el nombre del archivo")
        ########################
elif op == "2":
    '''
    struct message:
    dowload
        [b'cd', name]
    archivo no en el dominio
        [b'cd', b'ND', predecesor(ip:port)]
    '''
    name_file=input("Nombre de archivo a descargar: ") #se solicita el nombre del archivo a descargar
    if name_file in data_files.keys():
        for i in data_files[name_file]:
            socket.send_multipart([b'cd', bytes(i.encode())])
            message = socket.recv_multipart()
            while message[1].decode() == "ND":
                socket.disconnect(server)
                server = message[2].decode()
                socket.connect(server)
                socket.send_multipart([b'cd', bytes(i.encode())])
                message = socket.recv_multipart()
            if not(os.path.exists("Descargas")):
                os.mkdir("Descargas")
            try:
                f=open("Descargas"+"/"+name_file,"ab")
            except:
                f=open("Descargas"+"\\"+name_file,"ab")
            f.write(message[1])
            f.close()
        print("Archivo recibido")
    else:
        print("No cuenta con el archivo que quiere descargar")