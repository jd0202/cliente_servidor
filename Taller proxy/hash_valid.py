import hashlib

def md5Hash(filename1: str,filename2: str) -> str:
    md5_hash = hashlib.md5()
    with open(filename1,"rb") as f:
        # Read and update hash in chunks of 1K
        for byte_block in iter(lambda: f.read(1024*1024*1024),b""):
            md5_hash.update(byte_block)
    with open(filename2, "rb") as f1:
        for byte_block in iter(lambda: f1.read(1024*1024*1024),b""):
            md5_hash.update(byte_block)
        #return md5_hash.hexdigest()
    print(md5_hash.hexdigest())

md5Hash("476f3a5e96e4f3637f4c14469bdae72a_1","476f3a5e96e4f3637f4c14469bdae72a_2")
