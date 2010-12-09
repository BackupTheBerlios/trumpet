# UDP server example
import socket
from threading import Thread
##import pickle  
##import cPickle as pickle
import pickle

lista_clientes = []

class recibir_mensajes(Thread):
    def __init__(self,server_socket):
        Thread.__init__(self)
        self.server_socket = server_socket
 
    # Bucle para atender al cliente.       
    def run(self):
        while 1:
            data, address = self.server_socket.recvfrom(256)
            if data == "Conexion":
                lista_clientes.append(address[1])
##                diccionario = {"Tipo": "cliente", "numero": address[1]}
                diccionario = {"Tipo": "cliente", "numero": lista_clientes}
                mensaje = pickle.dumps (diccionario)
                for i in lista_clientes:
                    if i<>lista_clientes[0]:
                        server_socket.sendto(mensaje, ("localhost",i))
            print "( " ,address[0], " " , address[1] , " ) said : ", data
            
    

if __name__ == '__main__':

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind(("", 5000))
        lista_clientes.append(5000)
        print"Escribe broadcast para mandar un mensaje personal a todos los servidores"
        print"Escribe privado para mandar un mensaje privado a un cliente"
        print"Escribe actualizar, para actualizar la lista de clientes"
        print"UDPServer esperando conexiones en el puerto 5000................"

       # Se crea la clase con el hilo y se arranca.
        hilo = recibir_mensajes(server_socket)
        hilo.start()
        
        while 1:
            data = raw_input(">")
##          Broadcast que envia la lista de clientes a todos los clientes
            if data == "actualizar":
##          Tipo de datos que contiene el tipo de mensaje, y su contenido
                diccionario = {"Tipo": "actualizar", "numero": lista_clientes}
                print "Lista clientes del servidor: ",lista_clientes
                pickledList = pickle.dumps ( diccionario)
                for i in lista_clientes:
                    if i<>lista_clientes[0]:
                       server_socket.sendto(pickledList, ("localhost",i))
                       
            elif data == "privado":
##              Si no es broadcast, manda un mensaje a un cliente determinado 
                print "Lista de clientes del servidor: ",lista_clientes
                dir_cliente = raw_input("Introduce el cliente >")
                mensaje = raw_input("Introduce el mensaje >")
                diccionario = {"Tipo": "Mensaje", "numero": mensaje}
                pickledList = pickle.dumps ( diccionario)
                server_socket.sendto(pickledList, ("localhost",int(dir_cliente)))
                 
     
            if data == "broadcast":
                mensaje = raw_input("Introduce el mensaje >")
##          Tipo de datos que contiene el tipo de mensaje, y su contenido
                diccionario = {"Tipo": "broadcast", "numero": mensaje}
                pickledList = pickle.dumps ( diccionario)
                for i in lista_clientes:
                    if i<>lista_clientes[0]:
                       server_socket.sendto(pickledList, ("localhost",i))
    
