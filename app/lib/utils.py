from email.message import Message
from sys import platform
from socket import gethostbyname, gethostname, gaierror

GB = 1024 * 1024 * 1024


class MaxBodySizeException(Exception):
    def __init__(self, body_len: str, *args):
        super().__init__(*args)
        self.body_len = body_len


class MaxBodySizeValidator:
    def __init__(self, max_size: int):
        self.max_size = max_size
        self.body_len = 0

    def __call__(self, chunk: bytes):
        self.body_len += len(chunk)
        if self.body_len >= self.max_size:
            raise MaxBodySizeException(
                self.body_len, "The file's size is over the limit"
            )


def get_ip():
    if platform == 'darwin':
        host_ip = '127.0.0.1'
    else:
        try:
            host_ip = gethostbyname(gethostname())
        except gaierror:
            host_ip = '0.0.0.0'
    return host_ip


def parse_content_type(content_type: str) -> str:
    email = Message()
    email['content-type'] = content_type
    params = email.get_params()
    return params[0][0]
