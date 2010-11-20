#!/usr/bin/python
import socket
import threading
import time

def client(ip, port, num):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    talk(sock,num)
    sock.close()

def ask(sock,message):
    print message #XXX
    sock.send(message)
    response = sock.recv(1024)
    print response #XXX
    return response

def talk(sock,num):
    login = "xxx%d" % num
    pos = "0.0,0.0,1"
    destination = "0.0,0.%d,1" %num
    instructions = "please"
    response = ask(sock,("login=%s pos=%s destination=%s instructions=%s" % (login,pos,destination,instructions)))
    print "%s Received: %s" % (login,response) #XXX


if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    ip, port = "localhost", 9000
    for  i in range(0, 10):
        t = threading.Thread(target=client, args=(ip, port,  i, ))  
        t.start() 

