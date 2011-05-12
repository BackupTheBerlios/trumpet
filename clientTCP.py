#!/usr/bin/env python
 
import socket
from threading import Thread


lista_clientes = [5000]
mensaje = ""
ip_actual = 5001
lista_posiciones =[{"px": -61.5693,"py": 240.5599,"pz": 3.27917}]
lista_orientacion =[{"ow":0,"ox": 1,"oy":0,"oz": 1}]
lista_movimientos = []
mensaje_servidor = "ninguno"

#cliente para escribir por pantalla
class Recibir(Thread):
        def __init__(self, clientsocket):
                Thread.__init__(self)
                self.clientsocket = clientsocket
           
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
                        newdata = self.clientsocket.recv(1024) # recibimos los datos que envie el servidor
                        print 'servidor: %s',newdata # y con esto lo escribimos en pantalla


class Cliente():
        def __init__(self):
                # creamos el socket
                self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # ahora acemos que se conecte con el servidor
                self.clientsocket.connect(('localhost',5000))
                hilo = Recibir(self.clientsocket)
                hilo.start()  
                # este bucle hace que mientras este conectado  haga lo que pone en el interior
                while 1:
                        data = raw_input('>') #f uncion que hace que podamos escribir para mandarlo posteriormente
                        self.clientsocket.sendto(data, ("localhost",8000)) # enviamos los dtaos que hemos escrito
                        

if __name__ == '__main__':

        cliente = Cliente()
