#!/usr/bin/python
import socket
import threading

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    sock.send(message)
    response = sock.recv(1024)
    print "Received: %s" % response
    sock.close()


if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    ip, port = "localhost", 9000

    client(ip, port, "Hello World 1")
    client(ip, port, "Hello World 2")
    client(ip, port, "Hello World 3")



