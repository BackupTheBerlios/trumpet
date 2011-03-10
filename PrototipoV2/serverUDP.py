# UDP server example
import socket
from threading import Thread
##import pickle  
##import cPickle as pickle
import pickle

lista_clientes = []
lista_posiciones = []
lista_orientacion = []
lista_movimientos = [[]]
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
                lista_posiciones.append({"px": -61.5693,"py": 240.5599,"pz": 3.27917})
                lista_orientacion.append({"ow":0,"ox":1,"oy": 0,"oz": 1})
                
                for i in lista_clientes:
                    lista_movimientos.append([])
##                diccionario = {"Tipo": "cliente", "numero": address[1]}
                for i in lista_clientes:
                    if i<>lista_clientes[0]:
            ##          Tipo de datos que contiene el tipo de mensaje, y su contenido
                        diccionario = {"Tipo": "actualizar_lista_clientes", "lista_clientes": lista_clientes}
#                        ####print "Lista clientes del servidor: ",lista_clientes
                        pickledList = pickle.dumps ( diccionario)
                        server_socket.sendto(pickledList, ("localhost",i))
                               
            ##          Tipo de datos que contiene el tipo de mensaje, y su contenido
                        diccionario = {"Tipo": "actualizar_lista_posiciones","lista_posiciones":lista_posiciones}
#                        ####print "Lista posiciones: ",lista_posiciones
                        pickledList = pickle.dumps ( diccionario)
                        server_socket.sendto(pickledList, ("localhost",i))
                        
                        
                                ##          Tipo de datos que contiene el tipo de mensaje, y su contenido
                        diccionario = {"Tipo": "actualizar_lista_orientacion","lista_orientacion":lista_orientacion}
#                        ####print "Lista posiciones: ",lista_orientacion
                        pickledList = pickle.dumps ( diccionario)
                        server_socket.sendto(pickledList, ("localhost",i))
                        
                                                        ##          Tipo de datos que contiene el tipo de mensaje, y su contenido
                        diccionario = {"Tipo": "actualizar_lista_movimientos","lista_movimientos":lista_movimientos}
#                        ####print "Lista posiciones: ",lista_orientacion
                        pickledList = pickle.dumps ( diccionario)
                        server_socket.sendto(pickledList, ("localhost",i))

    
            else :
                mensaje = pickle.loads (data)
                if mensaje["Tipo"] == "broadcast":
                        if mensaje["Accion"]=="posicion":
#                            ####print mensaje
                            diccionario_posiciones = {"px": mensaje["px"],"py": mensaje["py"],"pz": mensaje["pz"]}
                            lista_posiciones[mensaje["posicion"]]=diccionario_posiciones
#                            ####print "El cliente" ,address[1], " esta en la posicion " ,mensaje["px"] , ",", mensaje["py"],",",mensaje["pz"]  
                            
                        if mensaje["Accion"]=="orientacion":
#                            ####print mensaje
                            diccionario_orientacion = {"ow": mensaje["ow"],"ox": mensaje["ox"],"oy": mensaje["oy"],"oz": mensaje["oz"]}
                            lista_orientacion[mensaje["posicion"]]=diccionario_orientacion
#                            ####print "El cliente" ,address[1], " esta en la posicion " ,lista_orientacion[mensaje["posicion"]]  
                            
                        if mensaje["Accion"]=="Accion":
#                            ####print mensaje
                            lista = lista_movimientos[mensaje["posicion"]]
                            lista.append(mensaje["Tipo_accion"])
                            lista_movimientos[mensaje["posicion"]]=lista
                            ####print "El cliente" ,address[1], " ha hecho estosmovimientos" ,lista_movimientos[mensaje["posicion"]]    
                    
            

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

            if data == "Posicion":

#                for i in lista_posiciones:
                   ####print i
                lista_posiciones[0]
                       
                       
            if data == "actualizar":
                for i in lista_clientes:
                    if i<>lista_clientes[0]:
                        diccionario = {"Tipo": "cliente", "numero": lista_clientes}
                        mensaje = pickle.dumps (diccionario)
                        server_socket.sendto(mensaje, ("localhost",i))
            ##          Tipo de datos que contiene el tipo de mensaje, y su contenido
                        diccionario = {"Tipo": "actualizar_lista_clientes", "lista_clientes": lista_clientes}
                        ####print "Lista clientes del servidor: ",lista_clientes
                        pickledList = pickle.dumps ( diccionario)
                        
                        for i in lista_clientes:
                            if i<>lista_clientes[0]:
                               server_socket.sendto(pickledList, ("localhost",i))
                               
                                    ##          Tipo de datos que contiene el tipo de mensaje, y su contenido
                        diccionario = {"Tipo": "actualizar_lista_posiciones","lista_posiciones":lista_posiciones}
                        ####print "Lista posiciones: ",lista_clientes
                        pickledList = pickle.dumps ( diccionario)
                        for i in lista_clientes:
                            if i<>lista_clientes[0]:
                               server_socket.sendto(pickledList, ("localhost",i))
                       
            elif data == "privado":
##              Si no es broadcast, manda un mensaje a un cliente determinado 
                ####print "Lista de clientes del servidor: ",lista_clientes
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
                
