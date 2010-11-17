#!/usr/bin/python
import socket
import threading
import SocketServer
import time


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    ''' Method that should take care of processing a request'''
    def process(self, pict):
        instr = ""
        if pict["destination"] == pict["pos"]:
            instr = "You reached your destination"
        else:
            instr = "Just go ahead and leave me alone, please"
        return instr
        
    def getDictValues(self,dic,values):
        string_values = ''
        for field in values:
            if field in dic:
                string_values = string_values+field+"="+dic.get(field)+' '
        string_values = string_values[0:-1] #Hack to remove last whitespace
        print string_values
        return string_values
    

    def talk(self):
        pict = {}
        data = self.request.recv(1024)
        answer = data.split()
        for item in answer:
            v = item.split('=')
            if v[0] and v[1] and not v[0] in pict:
                pict[v[0]] = v[1]
        print pict #XXX
        time.sleep(2) #XXX
        self.request.send(self.process(pict))


    def handle(self):
        self.talk()

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 9001

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    #server_thread.setDaemon(True)
    server_thread.start()
    print "Server loop running in thread:", server_thread.getName() #XXX

#    server.shutdown()
