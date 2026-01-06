from protocalhandler import ProtocolHandler
from server import Server
import socket

class Client(object):
    def __init__(self, host="127.0.0.1", port=31337):
        self._host = host
        self._port = port
        self._socket = None
        self._socket_file = None
        self._protocol = ProtocolHandler()

    def connect(self):
        # create a socket to connect to the server
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the server
        self._socket.connect((self._host, self._port))
        self._socket_file = self._socket.makefile('rwb')

    def disconnect(self):
        # close the file
        if self._socket_file:
            self._socket_file.close()
        if self._socket:
            self._socket.close()
    
    def execute(self, *args):
        pass