import hashlib

def md5Hash(filename: str) -> str:
    md5_hash = hashlib.md5()
    with open(filename,"rb") as f:
        # Read and update hash in chunks of 1K
        for byte_block in iter(lambda: f.read(1024*1024*1024),b""):
            md5_hash.update(byte_block)
        return md5_hash.hexdigest()