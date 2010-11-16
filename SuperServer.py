#!/usr/bin/python
import socket
import threading
import SocketServer
import time


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def process(self, pict):
        instr = ""
        if pict["destination"] == pict["pos"]:
            instr = "You reached your destination"
        else:
            instr = "Just go ahead and leave me alone, please"
        return instr
        

    def talk(self):
        pict = {}
        data = self.request.recv(1024)
        answer = data.split()
        for item in answer:
            v = item.split('=')
            if not v[0] in pict:
                pict[v[0]] = v[1]
        print pict
        #XXX
        time.sleep(2)
        self.request.send(self.process(pict))


    def handle(self):
        self.talk()

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 9000

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    #server_thread.setDaemon(True)
    server_thread.start()
    print "Server loop running in thread:", server_thread.getName()

#    server.shutdown()
