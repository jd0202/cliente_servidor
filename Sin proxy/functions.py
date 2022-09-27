import hashlib
import random
import socket as sk
import string
import json


def sha1Hash(filename: str) -> str:
    sha1_hash = hashlib.sha1()
    with open(filename,"rb") as f:
        # Read and update hash in chunks of 1K
        for byte_block in iter(lambda: f.read(1024*1024*1024),b""):
            sha1_hash.update(byte_block)
        return sha1_hash.hexdigest()

def get_ip(): #funcion para obtener la direccion ip del equipo
    s = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
    s.connect(("8.8.8.8",80))
    addr = "tcp://"+s.getsockname()[0]
    s.close()
    return addr

def get_id(): #funcion para generar el id del servidor
    s = ""
    nitems = random.randint(4,99)
    for _ in range(nitems):
        i = random.randrange(7)
        nitems = random.randint(1,99)
        if i == 0:
            for i in range(nitems):
                s = s + random.choice(string.ascii_uppercase)
        elif i == 1:
            for i in range(nitems):
                s = s + random.choice(string.digits)
        elif i == 2:
            for i in range(nitems):
                s = s + random.choice(string.ascii_lowercase)
        elif i == 3:
            for i in range(nitems):
                s = s + random.choice(string.hexdigits)
        elif i == 4:
            for i in range(nitems):
                s = s + random.choice(string.punctuation)
        elif i == 5:
            for i in range(nitems):
                s = s + random.choice(string.octdigits)
        elif i == 6:
            for i in range(nitems):
                s = s + random.choice(string.whitespace)
    #return int(hashlib.sha1(s.encode()).hexdigest(),16)
    return to_int(hashlib.sha1(s.encode()).hexdigest())

def to_int(hex): #funcion para pasar de hex a int
    return int(hex,16)

def save_file_info(data,name_json): #Funcion para guardar el diccionario de informacion en el json
    with open(name_json, "w") as newfiles:
        json.dump(data, newfiles, indent=4)