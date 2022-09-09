
import time
import os
import zmq
import json
import math
import socket as sk


'''
0: Archivo recibido
1: Ya existe el archivo
2: Ya existe un archivo con ese mismo nombre
3: Su usuario no cuenta con el archivo que quiere descargar

cx : cliente
    u: upload
    d:download
sx : server
'''

context = zmq.Context()
socket = context.socket(zmq.REP)
ip = "tcp://"+sk.gethostbyname(sk.gethostname())
#ip = "tcp://"+input("ingrese la su direccion ip")
#socket.bind("tcp://*:5555")
print("Proxy in: "+ip+":5555")
socket.bind(ip+":5555")


servers = list() #listado de servidores en linea

'''
struct message:
1)serve:
[id(sx),direccion:puerto...]
2)client:
    upload
        [id(cx),u,name_client,name_file,hash,num_all_parts...]
    dowload
        [id(cx),d,name_client,name_file...]
'''

###############################
#bloque de prueba
'''servers.append("serve1:puerto1")
servers.append("serve1:puerto2")'''
###############################

def save_file_info(data,name_json): #Funcion para guardar el diccionario de informacion en el json
    with open(name_json, "w") as newfiles:
        json.dump(data, newfiles, indent=4)

def answer_client(servers, parts_per_server,last_server): #funcion para organizar la respuesta del cliente
    answer =list()
    for i in servers:
        answer.append(bytes((i+"-"+str(parts_per_server)).encode()))
    if last_server > 0:
        answer[-1]=(bytes((i+"-"+str(last_server)).encode()))
    #print(answer)
    return answer
    
while True:
    #se abre y se carga la informacion de los archivos en la variable data
    with open("files.json") as files:
        data = json.load(files)
    
    with open("client.json") as files:
        data_client = json.load(files)
        
    message = socket.recv_multipart() # se recibe un mensaje de un cliente o un servidor

    if message[0].decode() == "sx": # se valida si el mensaje fue enviado por un servidor
        if not (message[1].decode() in servers):
            print("New serve: " +message[1].decode())
            servers.append(message[1].decode()) #se añada el servidor a la lista de servidores
        else:
            print("Reconected: "+message[1].decode())
        socket.send_string(" ")
    elif message[0].decode() == "cx": # se valida si el mensaje fue enviado por un cliente
        #se almacenan los datos del cliente y del archivo
        if message[1].decode() == "u":
            name_client = message[2].decode()
            name_file = message[3].decode()
            md5_hash = message[4].decode()
            num_all_parts = message[5].decode()
            parts_per_server = math.ceil(int(num_all_parts)/len(servers)) #calcula el numero de partes que el corresponde a cada server
            last_server=0
            if parts_per_server * len(servers) > int(num_all_parts): #en caso de que la division de partes no sea exacta se dejan las aprtes sobrantes para el ultimo server
                last_server = abs(parts_per_server * (len(servers)-1) - int(num_all_parts))
            else:
                last_server = 0
                
            '''
            data[hash]:[ num_all_part: #
                        clients[name_client]: name_file
                        direccion:puerto-parts
                        ]
            '''
            if name_client in data_client.keys():
                if name_file in data_client[name_client].keys():
                    socket.send_multipart([b'2']) #se responde con el codigo de que ya cuenta con un archivo con el mismo nombre
            if md5_hash in data.keys(): #se valida si ya existe el hash
                if name_client in data[md5_hash][1]: #se valida si un cliente trata de enviar el mismo archivo
                    socket.send_multipart([b'1']) #se responde con el codigo de que ya existe el archivo
                else:
                    #se asocia el nombre del cliente al hash del archivo para saber que otro cliente lo ha enviado
                    #data[md5_hash].add_client_name_file(name_client, name_file)
                    data[md5_hash][1][name_client] = name_file #se añade el nombre del nuevo clienet que envio un archivo ya existente
                    save_file_info(data,"files.json") #se guarda la informacion del archivo en el json
                    data_client[name_client][name_file] = md5_hash # se guarda informacion de los clientes y sus archivos en caso de que ueira descargarlos
                    save_file_info(data_client,"client.json")
                    socket.send_multipart([b'0']) #se responde con el codigo de archivo recibido
            else: # en caso de que no exista el hash se crea
                #data[md5_hash]= File(num_of_part, num_all_parts, name_client, name_file) 
                ans=answer_client(servers,parts_per_server,last_server)
                '''[direserver1:puertos1-parts_per_servers1, direserver2:puertos2-parts_per_servers2]'''
                print("To: "+name_client+" : "+str(ans))
                socket.send_multipart(ans) # se le indica al cliente a que servidor debe enviar las partes del archivo
                data[md5_hash] = [num_all_parts, {name_client:name_file}, [i.decode() for i in ans]] #se crea el nuevo hash
                save_file_info(data,"files.json") #se guarda la informacion del archivo en el json
                data_client[name_client] = {name_file:md5_hash} #se crea la informacion para el nuevo archivo
                save_file_info(data_client,"client.json")
        elif message[1].decode() == "d":
            name_client = message[2].decode()
            name_file = message[3].decode()
            if not(name_client in data_client.keys()):
                socket.send_multipart([b'3']) #se responde con el codigo de que no existe el archivo que desea descargar
            elif not(name_file in data_client[name_client].keys()):
                socket.send_multipart([b'3']) #se responde con el codigo de que no existe el archivo que desea descargar
            else:
                md5_hash = data_client[name_client][name_file]
                send_message = [i for i in data[md5_hash][2]]
                send_message.append(md5_hash)
                print("To : "+name_client+" : "+str(send_message))
                socket.send_multipart([i.encode() for i in send_message])