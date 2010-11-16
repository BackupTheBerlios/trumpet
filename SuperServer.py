#!/usr/bin/python
import socket
import threading
import SocketServer
import time


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def talk(self):
        while (True):
            data = self.request.recv(1024)
            answer = data.split()
            if answer:
                 if answer[0] == "bye":
                     self.request.send("Bye "+answer[1])
                     break
                 elif answer[0] == "login":
                     login = answer[1]
                     self.request.send("Hello "+answer[1])
                 elif answer[0] == "pos":
                     pos = answer[1]
                     self.request.send("POS "+answer[1])
                 elif answer[0] == "dest":
                     dest = answer[1]
                     self.request.send("DEST "+answer[1])
                 elif data == "instructions please":
                     self.request.send("Just Go Ahead")
                 else: self.request.send("Sorry?")

    def talk2(self):
        pict = {}
        data = self.request.recv(1024)
        answer = data.split()
        for item in answer:
            v = item.split('=')
            if not v[0] in pict:
                pict[v[0]] = v[1]
        print pict
        #XXX
        time.sleep(5)
        self.request.send("Just go ahead and leave me alone, please")


    def handle(self):
        self.talk2()
        #data = self.request.recv(1024)
        #cur_thread = threading.currentThread()
        #response = "%s: %s" % (cur_thread.getName(), data)
        #self.request.send(response)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    sock.send(message)
    response = sock.recv(1024)
    print "Received: %s" % response
    sock.close()

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

#    client(ip, port, "Hello World 1")
#    client(ip, port, "Hello World 2")
#    client(ip, port, "Hello World 3")

#    server.shutdown()
