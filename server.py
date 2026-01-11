from gevent import socket
from gevent.pool import Pool
from gevent.server import StreamServer

from protocalhandler import  ProtocolHandler, Disconnect, CommandError, Error

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
        print("connection established.....")
        while True:
            print("Waiting..")
            try:
                data = self._protocol.handle_request(socket_file)
            except Disconnect:
                break
            
            try:
              resp = self.get_response(data)
            except CommandError as exc:
                resp = Error(exc.args[0])
            
            self._protocol.write_response(socket_file, resp)
    
    def get_response(self,data):
        command = data[0].upper()

        if command == "GET":
            if len(data) != 2:
                raise CommandError("ERR Wrong number of arguments for GET")
            return self._kv.get(data[1])
        elif command == "SET":
            if len(data) != 3:
                raise CommandError("ERR Wrong number of arguments for SET")
            self._kv[data[1]] = data[2]
            return "OK"
        elif command == "DELETE":
            if len(data) != 2:
                raise CommandError("ERR Wrong number of arguments for DELETE")
            if data[1] in self._kv:
                del self._kv[data[1]]
                return 1
            return 0
        elif command == "PING":
            if len(data) != 1:
                raise CommandError("ERR Wrong number of arguments for PING")
            return "PONG"
        else:
            raise CommandError("ERR Unknown command %s" % command)

    def run(self):
        self._server.serve_forever()

if __name__ == "__main__":
    print("Sarting MiniRedis Server!")
    server = Server()
    server.run()