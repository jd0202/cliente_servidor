import sys
from uuid import getnode as get_mac
import os
import zmq
from funcions import *


address = hex(get_mac())[2:]
print(get_mac())
print('-'.join(address[i:i+2] for i in range(0, len(address), 2)))

context = zmq.Context()
socket = context.socket(zmq.REQ)

id = input("ingrese su id")
ip = get_ip()
port = input("Ingrese su puerto: ")
predecesor = input("ingrese la direccion y puerto de su predecesor")
print("id serve: "+str(id))
print("ip serve: "+ip)
print("puerto : "+port)
print("predecesor : "+predecesor)
rango=[0,0]

if predecesor == "-f":
    None
else:
    socket.connect(predecesor)
    

