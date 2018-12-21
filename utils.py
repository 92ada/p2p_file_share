import asyncio
import os
import mimetypes
import urllib
import re

TRACKER_IP = '192.168.123.29'

def get_file_list(root):
    result = []
    queue = [root]
    while queue != []:
        path = queue.pop(0)
        if os.path.isfile(path):
            result.append(path)
        else:
            queue.append(path)
