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
            queue.append(path)

def get_ip():
    return ([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])

def get_checksum(message) -> int:
    # sum of each 4 bytes, notice: not 2 bytes
    pass

def make_seed(path):
    data = open(path, "rb")

    # format: str(len) + ' ' + str(checksum)

def int_to_four_bytes(num):
    return (num).to_bytes(4, byteorder='big')

def four_bytes_to_int(bytes):
    return int.from_bytes(bytes, byteorder='big')
