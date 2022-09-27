import sys
from uuid import getnode as get_mac
import os
import zmq
import json
from functions import *

context = zmq.Context()
sockets = context.socket(zmq.REQ)
socketr = context.socket(zmq.REQ)

id = get_id()
ip = get_ip()
port = input("Ingrese su puerto: ")
my_ip = "tcp://" + ip + ":" + port
predecesor = input("ingrese la direccion y puerto de su predecesor: ")
id_predecesor = 0
ubicacion = input("ingrese el nombre de la carpeta a usar: ")
if not(os.path.exists(ubicacion)):
    os.mkdir(ubicacion)
print("id serve: "+str(id))
print("ip serve: "+ip)
print("predecesor : "+predecesor)
rango=[0,0]

'''
new server:
[b'sn, idserve, ip:port]

answer to new serve:
si el nodo esta a cargo de ese dominio:
[b'snp, predecesor(ip:port), id_predecesor]
si no: NC(no contenido)
[b'snp, b'NC(no contenido), next_nodo(ip:port9]


file to new serve:
[b'sf, idserve, name, file]
'''
if predecesor != "-f":
    predecesor = "tcp://" + predecesor 
    sockets.connect(predecesor)
    sockets.send_multipart([b'sn',bytes(id.encode())])
    message = sockets.recv()
    while message[1].decode == "NC":
        sockets.connect(message[2].decode())
        sockets.send_multipart([b'sn',bytes(id.encode())])
        message = sockets.recv()
    predecesor = message[2].decode()
    id_predecesor = int(message[3].decode())
    rango[1] == id

while True:
    try:
        with open(ubicacion+"/"+"files.json") as files:
            data_files = json.load(files)
    except:
        with open(ubicacion+"\\"+"files.json") as files:
            data_files = json.load(files)
    
    message = socketr.recv_multipart()
    if message[0].decode() == "sn":
        if int(message[1].decode()) > rango[0] and int(message[1].decode()) <= rango[1]:
            move_file = list()
            for i in data_files:
                if int(i) <= int(message[1].decode()):
                    move_file.append(i)
                    ############bloqeuar o no bloquear
            socketr.send_multipart([b'snp', bytes(predecesor.encode()), bytes(id_predecesor.encode()), [i.decode() for i in move_file]])
        else:
            socketr.send_multipart([b'snp', b'NC', bytes(predecesor.encode())])
    elif message[0].decode() == "sf":
        None
