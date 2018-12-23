import asyncio
import os
import mimetypes
import urllib
import re
import socket
import hashlib

TRACKER_IP = '20.21.11.26'
TRACKER_PORT = 30030
CHUNK_SIZE = 512
UPDATE_INTERVAL = 5


def get_file_list(root):
    '''Get file list from given path '''
    result = []
    queue = [root]
    while queue != []:
        path = queue.pop(0)
        if os.path.isfile(path):
            result.append(path)
        else:
            queue += [path + '/' + x for x in os.listdir(path)]
    return result

def get_seed_path(root, seed, id):
    '''Get path of given seed, if given id, only do partly hash'''
    print(seed)
    seed_list = seed.decode().split('\n')
    file_len = int(seed_list[1])
    print(type(id))
    hash_val = seed_list[id+3]
    queue = [root]
    while queue != []:
        path = queue.pop(0)
        if os.path.isfile(path):
            if os.path.getsize(path) == int(file_len):
                if id == -1:
                    if make_big_hash(path) == hash_val:
                        return path
                else:
                    with open(path, 'rb') as f:
                        f.seek(id*CHUNK_SIZE, 0)
                        data = f.read(CHUNK_SIZE)
                    if get_md5_hash(data) == hash_val:
                        return path
        else:
            queue += [path + '/' + x for x in os.listdir(path)]
    return None

# From stackoverflow
def get_ip():
    ''' Get ip address'''
    return ([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])

def get_md5_hash(data):
    ''' Get md5 hash value of data '''
    md5obj = hashlib.md5()
    md5obj.update(data)
    return md5obj.hexdigest()

def make_seed(path):
    # format: file_name + '\n' + str(file_len) + '\n' + big_hash \
    #           + '\n' + small_hash[0] + '\n' + ... + '\n' + small_hash[n]
    # notice: convert str above to bytes
    ''' Create a seed file from given path (and related file) 
            -Input: path
            -Output: encoded value 
    '''
    file_name = path.split('/')[-1]
    file_len = os.path.getsize(path)
    head = file_name + '\n' + str(file_len) + '\n'
    small_hash_list = ''
    big_hash_obj = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            data = f.read(CHUNK_SIZE)
            if not data: break
            small_hash = get_md5_hash(data)
            small_hash_list += '\n' + small_hash
            big_hash_obj.update(data)

    ret = head + big_hash_obj.hexdigest() + small_hash_list
    return ret.encode()

def make_big_hash(path):
    ''' Make hash for given file '''
    md5obj = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            data = f.read(CHUNK_SIZE)
            if not data: break
            md5obj.update(data)
    return md5obj.hexdigest()

def int_to_four_bytes(num):
    return (num).to_bytes(4, byteorder='big')

def four_bytes_to_int(bytes):
    return int.from_bytes(bytes, byteorder='big')



# Seems unnecessary to use checksum

# def get_checksum(data) -> int:
#     # sum of each 4 bytes, notice: not 2 bytes
#     while len(data) % 4 == 0:
#         data += b'\x00'
#
#     sum = 0
#     for idx in range(len(data)//4):
#         value = four_bytes_to_int(data[idx*4:idx*4+4])
#         sum += value
#         if sum > 4294967295:
#             sum -= 4294967295
#     return sum
