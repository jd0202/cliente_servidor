import hashlib
import socket as sk


def sha1Hash(filename: str) -> str:
    sha1_hash = hashlib.sha1()
    with open(filename,"rb") as f:
        # Read and update hash in chunks of 1K
        for byte_block in iter(lambda: f.read(1024*1024*1024),b""):
            sha1_hash.update(byte_block)
        return sha1_hash.hexdigest()

def get_ip():
    s = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
    s.connect(("8.8.8.8",80))
    addr = "tcp://"+s.getsockname()[0]
    s.close()
    return addr