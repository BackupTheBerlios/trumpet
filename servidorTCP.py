#!/usr/bin/env python
 
import socket
from threading import Thread

lista_clientes = [5000]
mensaje = ""
ip_actual = 5001
lista_posiciones =[]
lista_orientacion =[]
lista_movimientos = []
mensaje_servidor = "ninguno"
#cliente para escribir por pantalla
class Recibir(Thread):
        def __init__(self, clientsocket, clientaddress):
                Thread.__init__(self)
                self.clientsocket = clientsocket
                self.clientaddress = clientaddress
        # Bucle para atender al cliente.       
        def run(self):
                global lista_clientes
                global lista_posiciones
                global lista_orientacion
                global lista_movimientos
                global mensaje_servidor
                global mensaje
                global ip_actual
                while 1:
                        data = self.clientsocket.recv(1024) # recibimos datos del cliente
                        print 'cliente %s' % data # ponemos en pantalla lo que nos a dicho el cliente

class Accept(Thread):
        def __init__(self,serversocket):
                Thread.__init__(self)
                self.serversocket= serversocket
                
        def run(self):
                global lista_clientes
                while 1:
                        # aceptamos la conexion
                        clientsocket, clientaddress = self.serversocket.accept()
                        print 'Conexion desde: ', clientaddress # escribimos la ip del cliente
                        lista_clientes.append(clientaddress[1])
                        print lista_clientes
                        hilo = Recibir(clientsocket,clientaddress)
                        hilo.start()  
               

class Server():
        def __init__(self):
                global lista_clientes
                # creamos el socket
                self.serversocket    =   socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # usamos esta funcion para mantener en eschucha el puerto que queramos este caso 8000
                self.serversocket.bind(('localhost', 5000))
                # mantenemos en escucha el servidor
                self.serversocket.listen(10)
                print "Esperando clientes..."
                hiloAccept = Accept(self.serversocket)
                hiloAccept.start();
                # mientras estamos conectados hace lo que este dentro del bucle
                while 1:
                       #
                        newdata = raw_input('>') # escribimos lo que queramos enviar
##                        Con sendto eligiriamos a quien mandar los datos
##                        self.serversocket.sendto(newdata, ("192.168.1.255",5000)) # enviamos los dtaos que hemos escrito
##                        if not newdata: break # si no hay datos no lo enviamos
                        self.serversocket.send(newdata) # enviamos los dtaos que hemos escrito

##                clientsocket.close() # cerramos el socket

if __name__ == '__main__':
        server = Server()
