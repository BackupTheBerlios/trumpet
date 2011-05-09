# UDP client example
import socket
import time
import threading
##import pickle
import pickle
import sys



lista_clientes = [5000]
mensaje = ""
ip_actual = 5001
lista_posiciones =[{"px": -61.5693,"py": 240.5599,"pz": 3.27917}]
lista_orientacion =[{"ow":0,"ox": 1,"oy":0,"oz": 1}]
lista_movimientos = []
mensaje_servidor = "ninguno"
 

class thread_recibir(threading.Thread):
    def __init__(self,s):
        threading.Thread.__init__(self)
        self.socket = s
    def run(self):
        global lista_clientes
        global lista_posiciones
        global lista_orientacion
        global lista_movimientos
        global mensaje_servidor
        global mensaje
        global ip_actual
        while 1:
            

            data, address = self.socket.recvfrom(5000)
            mensaje = pickle.loads(data)

            if mensaje["Tipo"] == "actualizar_lista_clientes" :
                lista_clientes = mensaje["lista_clientes"]
#                print "Mensaje Broadcast: ",lista_clientes
            if mensaje["Tipo"] == "actualizar_lista_posiciones" :
                lista_posiciones = mensaje["lista_posiciones"]
#                print "Mensaje Broadcast: ",lista_posiciones
            if mensaje["Tipo"] == "actualizar_lista_orientacion" :
                lista_orientacion = mensaje["lista_orientacion"]
#                print "Mensaje Broadcast: ",lista_orientacion
            if mensaje["Tipo"] == "actualizar_lista_movimientos" :
                lista_movimientos = mensaje["lista_movimientos"]
#                print "Mensaje Broadcast: ",lista_movimientos
                
            if mensaje["Tipo"] == "privado" :
#                print mensaje["instruccion"]
                mensaje_servidor = mensaje["instruccion"]
                print "Mensaje Broadcast: ",mensaje_servidor
                
            if mensaje["Tipo"] == "broadcast":
                    if mensaje["Accion"]=="posicion":
#                        print mensaje
                        diccionario_posiciones = {"px": mensaje["px"],"py": mensaje["py"],"pz": mensaje["pz"]}
                        lista_posiciones[mensaje["posicion"]]=diccionario_posiciones
#                        print "El cliente" ,address[1], " esta en la posicion " ,mensaje["px"] , ",", mensaje["py"],",",mensaje["pz"]  
                        
                    if mensaje["Accion"]=="orientacion":
#                        print mensaje
                        diccionario_orientacion = {"ow": mensaje["ow"],"ox": mensaje["ox"],"oy": mensaje["oy"],"oz": mensaje["oz"]}
                        lista_orientacion[mensaje["posicion"]]=diccionario_orientacion
#                        print "El cliente" ,address[1], " esta en la posicion " ,lista_orientacion[mensaje["posicion"]]    
                        
                    if mensaje["Accion"]=="movimiento":
#                        print mensaje
                        lista = lista_movimientos[mensaje["posicion"]]
                        lista.append(mensaje["Tipo_accion"])
                        lista_movimientos[mensaje["posicion"]]=lista
#                        print "El cliente" ,address[1], " ha hecho estos movimientos" ,lista_movimientos[mensaje["posicion"]]         
                
            
class conectar():
    def __init__(self):


        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.sendto("Conexion", ("localhost",5000))
        self.recibir = thread_recibir(self.client_socket)
        #self.recibir.start()
        

#        print"Escribe lista para ver una lista de todos los clientes conectados"
#        print"Escribe mensaje para ver el mensaje actual que ha mandado el servidor"
        


        
    def getPosicionActual(self,i):
        global lista_posiciones
        return lista_posiciones[i]
    
    def getOrientacionActual(self,i):
        global lista_orientacion
        return lista_orientacion[i]

    def getListaMov(self):
        global lista_movimientos
        return lista_movimientos
        
    def getListaMovimientos(self,i):
        global lista_movimientos
        return lista_movimientos[i]
    
    def getMovimiento(self,i):
        global lista_movimientos
        return lista_movimientos[i].pop()
    
    def getMensaje(self):
        global mensaje_servidor
      
        return mensaje_servidor
    
    
    
    def getListaClientesServidor(self):

        return lista_clientes

        
    def getIp(self):
        global lista_clientes
        return lista_clientes[-1]
    
    def getFirstClient(self):
        global lista_clientes
        return lista_clientes[1]
    
    def getListaClientes(self):
        return lista_clientes
    
    def getListaPosiciones(self):
        return lista_posiciones
           
    def broadcast_posicion(self,lista_ip,px,py,pz):
                    
    ##          Tipo de datos que contiene el tipo de mensaje, y su contenido
        diccionario = {"Tipo": "broadcast","Accion": "posicion","posicion":lista_ip,"px" : px,"py" : py,"pz" :pz}
        pickledList = pickle.dumps ( diccionario)
        for i in lista_clientes:
            self.client_socket.sendto(pickledList, ("localhost",i))
        
        
    def broadcast_orientacion(self,lista_ip,ow,ox,oy,oz):
                    
    ##          Tipo de datos que contiene el tipo de mensaje, y su contenido
        diccionario = {"Tipo": "broadcast","Accion": "orientacion","posicion":lista_ip,"ow":ow,"ox": ox,"oy": oy,"oz":oz}
        pickledList = pickle.dumps ( diccionario)
        for i in lista_clientes:
            self.client_socket.sendto(pickledList, ("localhost",i))
            
    def broadcast_accion(self,lista_ip,accion):
        #print "ACCION"
    ##          Tipo de datos que contiene el tipo de mensaje, y su contenido
        diccionario = {"Tipo": "broadcast","Accion": "movimiento","posicion":lista_ip,"Tipo_accion":accion}
        pickledList = pickle.dumps ( diccionario)
        for i in lista_clientes:
            self.client_socket.sendto(pickledList, ("localhost",i))
            
    def run(self):
#
#        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#        client_socket.sendto("Conexion", ("localhost",5000))
#        recibir = thread_recibir(client_socket)
#        recibir.start()
#        print"Escribe lista para ver una lista de todos los clientes conectados"
#        print"Escribe mensaje para ver el mensaje actual que ha mandado el servidor"
        while 1:
    
                data = raw_input("> ")
                if data == "lista":
                    print lista_clientes
                if data == "mensaje":
                    print mensaje
                if data == "broadcast":
                    mensaje = raw_input("Introduce el mensaje >")
                    
    ##          Tipo de datos que contiene el tipo de mensaje, y su contenido
                    diccionario = {"Tipo": "broadcast", "numero": mensaje}
                    pickledList = pickle.dumps ( diccionario)
                    for i in lista_clientes:
                           client_socket.sendto(pickledList, ("localhost",i))

                if data <> "q" and data <> "Q":
                    self.client_socket.sendto(data, ("localhost",5000))
                     
                else:
                        break
        self.client_socket.close()
    
                


##        enviar = thread_enviar(client_socket)
##        enviar.start()
