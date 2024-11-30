from sys import platform
from socket import gethostbyname, gethostname, gaierror

GB = 1024 * 1024 * 1024

def get_ip():
    if platform == 'darwin':
        host_ip = '127.0.0.1'
    else:
        try:
            host_ip = gethostbyname(gethostname())
        except gaierror:
            host_ip = '0.0.0.0'
    return host_ip
