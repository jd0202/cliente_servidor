import os
import zmq
import socket as sk
import json

'''
0: Archivo recibido
1: Ya existe el archivo
'''

context = zmq.Context()

socket = context.socket(zmq.REQ)

'''
struct message:
1)serve:
[id(sx),direccion:puerto...]
'''

ip_proxy = "tcp://"+input("Ingrese la direccion del servidor proxy: ")
port_proxy = input("Ingrese el puerto del proxy: ")
proxy = ip_proxy+":"+port_proxy
#socket.connect("tcp://localhost:5555") # se conecta al servidor proxy
socket.connect(proxy) # se conecta al servidor proxy

s = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
s.connect(("8.8.8.8",80))
addr = "tcp://"+s.getsockname()[0]
s.close()

#addr = "tcp://"+sk.gethostbyname(sk.gethostname())
#addr = "tcp://"+input("ingrese su direccion ip: ") #se define una variable con el puerto
#addr = "tcp://localhost:" # se define una variable con la direccion ip
port = input("Ingrese su puerto: ") #se define una variable con el puerto
#port="1111" #se define una variable con el puerto
my_addr= addr+":"+port

ubicacion = input("ingrese el nombre de la carpeta a usar: ")

if not(os.path.exists(ubicacion)):
    os.mkdir(ubicacion)


print("Server in: "+my_addr)

socket.send_multipart([b'sx',bytes((my_addr).encode())])# se envia la informacion de el servidor al proxy direccion:puerto
socket.recv()

socket.close()#se cierra la conexion

socket = context.socket(zmq.REP)# se modifica el contex del socket

if addr == "tcp://localhost:":
    socket.bind("tcp//*:"+port)
else:
    socket.bind(addr+":"+port)
#socket.bind("tcp://*:"+port)# se inicia un nuevo socket con la direccion del servidor

while True:
    #  Wait for next request from client
    message = socket.recv_multipart() # se recibe el archivo que envia el cliente y el nombre del archivo
    if message[0].decode() == "u":
        name_file = message[1].decode() #se extrae el nombre del archivo
        try:
            f=open(ubicacion+"/"+name_file,"wb")
        except:
            f=open(ubicacion+"\\"+name_file,"wb")     
        #f=open(name_file,"wb") # se crea el archivo con el nombre que el cliente envio
        f.write(message[2]) #se escribe la informacion que envio el cliente
        print("archivo: "+name_file+" recibido")
        f.close()# se cierra el archivo
        socket.send_string(" ") #se envia al cliente un espacio para validar la recepcion y respuesta
    elif message[0].decode() == "d":
        name_file = message[1].decode() #se extrae el nombre del archivo
        print(name_file)
        try:
            f=open(ubicacion+"/"+name_file,"rb")
        except:
            f=open(ubicacion+"\\"+name_file,"rb")
        #f=open(name_file,"rb")
        contenido=f.read()
        socket.send_multipart([contenido])
        print("Send :"+name_file)


