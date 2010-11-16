#!/usr/bin/python
import socket
import threading
import SocketServer

class GiveTCPRequestHandler(SocketServer.BaseRequestHandler):

    def talk(self):
        data = self.request.recv(1024)
        if data == "pos 0.0,0.0,1 dest 0.0,0.1,1":
           response = "Go Ahead"
           self.request.send(response)
        

    def handle(self):
        self.talk()
        #data = self.request.recv(1024)
        #cur_thread = threading.currentThread()
        #response = "%s: %s" % (cur_thread.getName(), data)
        #self.request.send(response)

class GiveTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 9001

    server = GiveTCPServer((HOST, PORT), GiveTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    #server_thread.setDaemon(True)
    server_thread.start()
    print "Give Server loop running in thread:", server_thread.getName()

#    client(ip, port, "Hello World 1")
#    client(ip, port, "Hello World 2")
#    client(ip, port, "Hello World 3")

#    server.shutdown()
