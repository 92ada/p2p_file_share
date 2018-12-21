import asyncio
import os
import mimetypes
import urllib
import re
import socket

TRACKER_IP = '192.168.123.29'
BLOCK_SIZE = 64


def get_file_list(root):
    result = []
    queue = [root]
    while queue != []:
        path = queue.pop(0)
        if os.path.isfile(path):
            result.append(path)
        else:
            queue += [path + '/' + x for x in os.listdir(path)]
    return result

def get_seed_path(root, seed):
    file_len, checksum = seed.split(' ')
    queue = [root]
    while queue != []:
        path = queue.pop(0)
        if os.path.isfile(path):
            if os.path.getsize(path) == int(file_len):
                data = open(path, 'rb').read()
                if get_checksum(data) == int(checksum):
                    return path
        else:
            queue += [path + '/' + x for x in os.listdir(path)]
    return None

def get_ip():
    return ([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])

def get_checksum(data) -> int:
    # sum of each 4 bytes, notice: not 2 bytes
    while len(data) % 4 == 0:
        data += b'\x00'

    sum = 0
    for idx in range(len(data)//4):
        value = four_bytes_to_int(data[idx*4:idx*4+4])
        sum += value
        if sum > 4294967295:
            sum -= 4294967295
    return sum



def make_seed(path):
    # format: str(len) + ' ' + str(checksum)
    data = open(path, "rb").read()
    file_len = os.path.getsize(path)
    checksum = get_checksum(data)
    return str(len) + ' ' + str(checksum)

def int_to_four_bytes(num):
    return (num).to_bytes(4, byteorder='big')

def four_bytes_to_int(bytes):
    return int.from_bytes(bytes, byteorder='big')
