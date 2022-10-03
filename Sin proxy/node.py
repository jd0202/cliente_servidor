from socket import socket
import sys
from uuid import getnode as get_mac
import os
import zmq
import json
from functions import *

def save_data_file(data,file):
    try:
        save_file_info(data_files, ubicacion+"/"+file)
    except:
        save_file_info(data_files, ubicacion+"\\"+file)

context = zmq.Context()
sockets = context.socket(zmq.REQ)
socketr = context.socket(zmq.REP)

id = get_id() #funcion que genera un id aleatorio para el servidor
#####Bloque de prueba
#id =int(input("idserver?"))
#####
ip = get_ip() #funcion que optiene las ip del dispositivo
port = input("Ingrese su puerto: ")
my_ip = ip + ":" + port #se concatena la ip con el puerto a usar
server = "tcp://" + input("ingrese la direccion y puerto de un servidor: ")
ubicacion = input("ingrese el nombre de la carpeta a usar: ")
filesJson = "files.json" #archivo en donde se guardara la informacion d los archivos con los que cuenta el servidor
if not(os.path.exists(ubicacion)):
    os.mkdir(ubicacion)
    try:
        f=open(ubicacion+"/"+filesJson,"w")
        save_file_info(list(), ubicacion+"/"+filesJson)
    except:
        f=open(ubicacion+"\\"+filesJson,"w")
        save_file_info(list(), ubicacion+"\\"+filesJson)

print("id serve: "+str(id))
print("ip serve: "+ip)
print("server to in : "+server)
rango=[0,0]
socketr.bind(my_ip)

'''
new server:
[b'sn', idserve, ip:port]

answer to new serve:
si el nodo esta a cargo de ese dominio:
    si hay archivos para pasar:
        [b'snp', predecesor(ip:port), id_predecesor, [name_files]]
    si no:
        [b'snp', predecesor(ip:port), id_predecesor, b'nofiles']
si no: NC(no contenido)
    [b'snp', b'NC(no contenido), next_nodo(ip:port9]


solicitud de archivos de new serve:
[b'snf', idserve, name]
file to new serve:
[b'snf', name, file]

archivo desde un cliente
subida:
[b'cu', name, file]
bajada:
[b'cd', name]
archivo no en el dominio
[b'cd', b'ND', predecesor(ip:port)]
archivo si en el dominio
[b'cd', b'ok',file]
'''
files_to_request=[]

id_predecesor = id
predecesor = my_ip
id_sucesor = id
sucesor = my_ip
rango[0]=id
rango[1]=id

if server != "tcp://-f": #en caso de que NO ser el primer servidor
    sockets.connect(server) #se conceta a la direccion proporcionada
    sockets.send_multipart([b'sn', bytes(str(id).encode()), bytes(my_ip.encode())]) #se envia la notificacion de que se trata de un nuevo servidor
    message = sockets.recv_multipart() #se recibe la respuesta
    while message[1].decode() == "NC": #en caso de que el servidor no sea el que contiene el id del nuevo en el dominio se busca hasta encontrarlo
        if message[2].decode() == "N42":
            sys.exit("No existe el 42")
        sockets.disconnect(server)
        server = message[2].decode()
        sockets.connect(server)
        sockets.send_multipart([b'sn', bytes(str(id).encode()), bytes(my_ip.encode())])
        message = sockets.recv_multipart()
    predecesor = message[1].decode()
    id_predecesor = int(message[2].decode())
    print("id = " + str(id))
    print("predecesor id = " + str(id_predecesor))
    print("predecesor = " + predecesor)
    if message[3].decode() != "nofiles":
        files_to_request = [i.decode() for i in message[3:]]
    else:
        files_to_request = []
    rango[1] = id
    rango[0] = id_predecesor
    print("rango [0] ="+str(rango[0])+" rango[0] = "+str(rango[1]))

while True:
    try:
        with open(ubicacion+"/" + filesJson) as files:
            data_files = json.load(files)
    except:
        with open(ubicacion+"\\" + filesJson) as files:
            data_files = json.load(files)

    if files_to_request:
        sockets.send_multipart([b'snf', bytes(str(id).encode()), bytes(files_to_request[-1].encode())])
        files_to_request.pop()
        message = sockets.recv_multipart()
        name_file = message[1].decode()
        try:
            f=open(ubicacion+"/"+name_file,"wb")
        except:
            f=open(ubicacion+"\\"+name_file,"wb")
        f.write(message[2])
        print("archivo tranferido: "+name_file+" recibido")
        f.close()# se cierra el archivo
        data_files.append(name_file)
        save_data_file(data_files,filesJson)
    
    message = socketr.recv_multipart()
    #[b'sn', idserve, ip:port]
    if message[0].decode() == "sn": #si se trata de un mensaje de otro servidor
        id_recv = int(message[1].decode())
        ip_port_recv = message[2].decode()
        print("new serve: id = "+str(id_recv) +" ip = " + message[2].decode())
        if not(rango[0] < rango[1]) and id_recv > rango[0]: #en caso de que el nuevo servidor tenga un id mayor al del servidor que ya existe
            move_file = list()
            for i in data_files:
                int_i = to_int(i)
                if (int_i > rango[0]) and (int_i <= id_recv):
                    move_file.append(i)
            rango[0] = id_recv
            if move_file:
                #[b'snp', predecesor(ip:port), id_predecesor, sucesor(ip:port), id_sucesor,  [name_files]]
                socketr.send_multipart([b'snp', bytes(predecesor.encode()), bytes(str(id_predecesor).encode())] + [str(i).encode() for i in move_file])
            else:
                #[b'snp', predecesor(ip:port), id_predecesor, b'nofiles']
                socketr.send_multipart([b'snp', bytes(predecesor.encode()), bytes(str(id_predecesor).encode()), b'nofiles'])
            predecesor = ip_port_recv
            id_predecesor = id_recv
            print("id = " + str(id))
            print("predecesor id = " + str(id_predecesor))
            print("predecesor = " + predecesor)
            print("rango [0] ="+str(rango[0])+" rango[0] = "+str(rango[1]))
        elif not(rango[0] < rango[1]) and id_recv < rango[1]:
            move_file = list()
            for i in data_files:
                int_i = to_int(i)
                if (int_i > rango[1]) or (int_i <= id_recv):
                    move_file.append(i)
            rango[0] = id_recv
            if move_file:
                #[b'snp', predecesor(ip:port), id_predecesor, sucesor(ip:port), id_sucesor,  [name_files]]
                socketr.send_multipart([b'snp', bytes(predecesor.encode()), bytes(str(id_predecesor).encode())] + [str(i).encode() for i in move_file])
            else:
                #[b'snp', predecesor(ip:port), id_predecesor, b'nofiles']
                socketr.send_multipart([b'snp', bytes(predecesor.encode()), bytes(str(id_predecesor).encode()), b'nofiles'])
            predecesor = ip_port_recv
            id_predecesor = id_recv
            print("id = " + str(id))
            print("predecesor id = " + str(id_predecesor))
            print("predecesor = " + predecesor)
            print("rango [0] ="+str(rango[0])+" rango[0] = "+str(rango[1]))
        elif id_recv > rango[0] and id_recv <= rango[1]:
            move_file = list()
            for i in data_files:
                int_i = to_int(i)
                if int_i < rango[1]:
                    move_file.append(i)
            rango[0] = id_recv
            if move_file:
                #[b'snp', predecesor(ip:port), id_predecesor, sucesor(ip:port), id_sucesor,  [name_files]]
                socketr.send_multipart([b'snp', bytes(predecesor.encode()), bytes(str(id_predecesor).encode())] + [str(i).encode() for i in move_file])
            else:
                #[b'snp', predecesor(ip:port), id_predecesor, b'nofiles']
                socketr.send_multipart([b'snp', bytes(predecesor.encode()), bytes(str(id_predecesor).encode()), b'nofiles'])
            predecesor = ip_port_recv
            id_predecesor = id_recv
            print("id = " + str(id))
            print("predecesor id = " + str(id_predecesor))
            print("predecesor = " + predecesor)
            print("rango [0] ="+str(rango[0])+" rango[0] = "+str(rango[1]))
        elif id_recv == id:
            socketr.send_multipart([b'snp', b'NC', b'N42'])
        else:
            print("idserve no en mi dominio")
            socketr.send_multipart([b'snp', b'NC', bytes(predecesor.encode())])

    #####sin testear
    elif message[0].decode() == "snf":
        name_file = message[2].decode()
        try:
            f=open(ubicacion+"/"+name_file,"rb")
        except:
            f=open(ubicacion+"\\"+name_file,"rb")
        contenido=f.read()
        socketr.send_multipart([b'snf', bytes(name_file.encode()), contenido])
        f.close()
        print("archivo tranferido: "+name_file+" enviado")
        try:
            os.remove(ubicacion+"/"+name_file)
        except:
            os.remove(ubicacion+"\\"+name_file)
        data_files.remove(name_file)
        save_data_file(data_files,filesJson)
    ######

    #[b'cu', name, file]
    elif message[0].decode() == "cu":
        name_file = message[1].decode()
        id_file = to_int(name_file)
        print("file : "+str(id_file))
        if (not(rango[0] < rango[1]) and (id_file > rango[0] or id_file <= rango[1])) or (id_file > rango[0] and id_file <= rango[1]):
        #if id_file in data_files:
            if name_file in data_files:
                print("archivo: "+name_file+" ya existente")   
            else: 
                data_files.append(name_file)
                save_data_file(data_files,filesJson)
                try:
                    f=open(ubicacion+"/"+name_file,"wb")
                except:
                    f=open(ubicacion+"\\"+name_file,"wb")  
                f.write(message[2]) #se escribe la informacion que envio el cliente
                print("archivo: "+name_file+" recibido")
                f.close()# se cierra el archivo
            socketr.send_multipart([b'cu', b'', bytes(predecesor.encode())])#se envia al cliente un espacio para validar la recepcion y respuesta
        else:
            print("file no para mi dominio")
            socketr.send_multipart([b'cu', b'ND', bytes(predecesor.encode())])
    #[b'cd', name]
    #archivo si en el dominio:
    #[b'cd', b'ok',file]
    elif message[0].decode() == "cd":
        name_file = message[1].decode()
        id_file = to_int(name_file)
        if name_file in data_files:
            print(name_file)
            try:
                f=open(ubicacion+"/"+name_file,"rb")
            except:
                f=open(ubicacion+"\\"+name_file,"rb")
            contenido=f.read()
            socketr.send_multipart([b'cd', b'ok', contenido])
            print("Send :"+name_file)
        else:
            print("file no para mi dominio")
            socketr.send_multipart([b'cu', b'ND', bytes(predecesor.encode())])