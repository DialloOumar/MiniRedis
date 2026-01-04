from gevent import socket
from gevent.pool import Pool
from gevent.server import StreamServer

from collections import namedtuple
from io import BytesIO
from socket import error as socket_error


class CommandError(Exception): pass
class Disconnect(Exception): pass

Error = namedtuple("Error", ("message",))


class ProtocolHandler(object):
    def __init__(self):
        self.handlers = {
            b'+': self.handle_simple_string,
            b'-': self.handle_error,
            b':': self.handle_integer,
            b'$': self.handle_bulk_string,
            b'*': self.handle_array,
        }

    def handle_request(self,socket_file):
        # Reading the first byte
        first_byte = socket_file.read(1)

        if not first_byte:
            raise Disconnect()
        
        resp = self.handlers[first_byte](socket_file)
        return resp

    def handle_simple_string(self,socket_file):
        return str(self._read_line(socket_file))

    def handle_error(self, socket_file):
        msg = str(self._read_line(socket_file))
        return Error(msg)
    
    def handle_integer(self, socket_file):
        return int(self._read_line(socket_file))
    
    def _read_line(self, socket_file):
        line = []
        ch=b'1'
        while  ch != b'':
            # We start reading
            ch = socket_file.read(1)
            # We check if we are at terminating character
            if ch == b'\r':
                next_ch = socket_file.read(1)
                if next_ch == b'\n':
                    break # We have found the terminating charters \r\n
                else:
                    line.append(ch)
                    line.append(next_ch)
            else:
                line.append(ch)
        
        return b''.join(line).decode('utf-8')
    
    def handle_bulk_string(self, socket_file):
        # Read the length of the string to read
        length = int(self._read_line(socket_file))
        if length == -1:
            return None
        
        # Step 3: Read exactly 'length' bytes
        data = socket_file.read(length)

        # Read the trailing \r\n
        socket_file.read(2)

        # return the string version by decoding
        return data.decode('utf-8')

    def handle_array(self, socket_file):
        # Get the size of the array
        size = int(self._read_line(socket_file))
        if size == -1: 
            return None
        elif size < -1:
            raise CommandError("Invalid Command")
        
        arr = []
        while size > 0:
            arr.append(self.handle_request(socket_file))
            size -= 1
        return arr

    def write_response(self,socket_file,data):

        resp = ''
        if isinstance(data, int):
            resp = ':%s\r\n' % data
        elif isinstance(data,str):
            resp = '$%s\r\n%s\r\n' % (len(data),data)
        elif isinstance(data, list):
            resp = '*%s\r\n'% len(data)
            socket_file.write(resp.encode('utf-8'))
            for elm in data:
                self.write_response(socket_file,elm)
            socket_file.flush()
            return
        elif isinstance(data,Error):
            resp = '-%s\r\n' % data.message
        elif data is None:
            resp = '$-1\r\n'

        socket_file.write(resp.encode('utf-8'))
        socket_file.flush()

class Server(object):
    def __init__(self, host="127.0.0.1", port=31337, max_client=64):
        self._pool = Pool(max_client)
        self._server = StreamServer(
            (host,port), 
            self.connection_handler,
            spawn=self._pool)
        self._protocol = ProtocolHandler()
        self._kv = {}
    
    def connection_handler(self,conn, address):
        socket_file = conn.makefile('rwb')

        while True:
            try:
                data = self._protocol.handle_request(socket_file)
                break
            except Disconnect:
                break

            # try:
            #     resp = self.get_response(data)
            # except CommandError as exc:
            #     resp = Error(exc.args[0])
            
            # self._protocol.write_response(socket_file, resp)
    
    def get_response(self,data):
        pass

    def run(self):
        self._server.serve_forever()

if __name__ == "__main__":
    print("Hello miniRedis!")