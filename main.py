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

    def handle_error(self, socket_file):
        print("Error")
    
    def handle_integer(self, socket_file):
        print("Integer")
    
    def handle_bulk_string(self, socket_file):
        print("Bulk String")

    def handle_array(self, socket_file):
        print("Array")

    def write_response(self,socket_file,data):
        pass

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
    
    # Test the protocol handler
    print("\n=== Testing Protocol Handler ===")
    
    # Create a fake socket file using BytesIO
    from io import BytesIO
    
    # Test 1: Simple String
    print("\nTest 1: Simple String")
    fake_data = BytesIO(b'+OK\r\n')
    handler = ProtocolHandler()
    result = handler.handle_request(fake_data)
    print(f"Input: +OK\\r\\n")
    print(f"Result: {result}")
    print(f"Expected: OK")
    
    # Test 2: Another Simple String
    print("\nTest 2: Simple String - Hello")
    fake_data = BytesIO(b'+Hello World\r\n')
    result = handler.handle_request(fake_data)
    print(f"Input: +Hello World\\r\\n")
    print(f"Result: {result}")
    print(f"Expected: Hello World")