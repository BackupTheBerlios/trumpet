#!/usr/bin/python
import socket
import threading
import time

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    talk2(sock)
   # sock.send(message)
   # response = sock.recv(1024)
   # print "Received: %s" % response
    sock.close()

def ask(sock,message):
    print message
    sock.send(message)
    response = sock.recv(1024)
    print response
    return response

def talk(sock):
    login = "xxx1"
    pos = "0.0,0.0,1"
    destination = "0.0,0.1,1"
    response = ask(sock,"login "+login)
    if (response == ("Hello " + login)):
        response = ask(sock,"pos "+pos)
        if (response == ("POS " + pos)):
            response = ask(sock,"dest "+destination)
            if (response == ("DEST " + destination)):
                response = ask(sock, "instructions please")
                print "Received: %s" % response

def talk2(sock):
    login = "xxx1"
    pos = "0.0,0.0,1"
    destination = "0.0,0.1,1"
    instructions = "please"
    response = ask(sock,("login=%s pos=%s destination=%s instructions=%s" % (login,pos,destination,instructions)))
    print "Received: %s" % response


if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    ip, port = "localhost", 9000

    client(ip, port, "Hello World 1")
    client(ip, port, "Hello World 2")
    client(ip, port, "Hello World 3")



