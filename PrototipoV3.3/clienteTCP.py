#!/usr/bin/env python
 
import socket
from threading import Thread
import pickle


lista_clientes = [5000]
mensaje = ""
ip_actual = 5001
lista_posiciones =[{"px": -61.5693,"py": 240.5599,"pz": 3.27917}]
lista_orientacion =[{"ow":0,"ox": 1,"oy":0,"oz": 1}]
lista_movimientos = [[]]
lista_ultimo_mov=['null']
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
                global lista_ultimo_mov
                global mensaje_servidor
                global mensaje
                global ip_actual
                while 1:
                    peticion = self.clientsocket.recv(1024) # recibimos los datos que envie el servidor
                    mensaje = pickle.loads (peticion)
                    if mensaje["Tipo"] == "actualizar_lista_clientes" :
                        lista_clientes = mensaje["lista_clientes"]
#                        print "lista_clientes: ",lista_clientes
                    if mensaje["Tipo"] == "actualizar_lista_posiciones" :
                        lista_posiciones = mensaje["lista_posiciones"]
                        lista_orientacion = mensaje["lista_orientacion"]
#                        print "lista_posiciones: ",lista_posiciones
                    if mensaje["Tipo"] == "actualizar_lista_orientacion" :
                        lista_orientacion = mensaje["lista_orientacion"]
#                        print "lista_orientacion: ",lista_orientacion
                    if mensaje["Tipo"] == "actualizar_lista_movimientos" :
                        lista_movimientos = mensaje["lista_movimientos"]
                        lista_ultimo_mov = mensaje["lista_movimientos"]
#                        print "lista_movimiento: ",lista_ultimo_mov

class conectar():
        def __init__(self):
                # creamos el socket
                self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # ahora acemos que se conecte con el servidor
                self.clientsocket.connect(('localhost',4443))
                self.recibir = Recibir(self.clientsocket)
##                hilo.start()  
                # este bucle hace que mientras este conectado  haga lo que pone en el interior
##                while 1:
##                        data = raw_input('>') #f uncion que hace que podamos escribir para mandarlo posteriormente
##                        self.clientsocket.send(data) # enviamos los dtaos que hemos escrito

        def getPosicionActual(self,i):
                global lista_posiciones
                return lista_posiciones[i]
    
        def getOrientacionActual(self,i):
                global lista_orientacion
                return lista_orientacion[i]

        def getListaClientes(self):
                return lista_clientes
           
        def getListaMov(self):
             global lista_movimientos
             return lista_movimientos
        
        def getListaMovimientos(self,i):
             global lista_movimientos
             return lista_movimientos[i]
        
        def setUltimoMov(self,i,valor):
             global lista_ultimo_mov
             lista_ultimo_mov[i] = valor
             
        def getUltimoMov(self,i):
             global lista_ultimo_mov
#             print  lista_ultimo_mov
             valor = lista_ultimo_mov[i]
             lista_ultimo_mov[i] = "null"
             return valor
    
        def getListaUltimoMovimiento(self):
             global lista_ultimo_mov
             return lista_ultimo_mov
        
        def getMovimiento(self,i):
             global lista_movimientos
             return lista_movimientos[i].pop()

#        def broadcast_posicion(self,lista_ip,px,py,pz):
#                    
#    ##          Tipo de datos que contiene el tipo de mensaje, y su contenido
#                diccionario = {"Tipo": "broadcast","Accion": "posicion","posicion":lista_ip,"px" : px,"py" : py,"pz" :pz}
#                pickledList = pickle.dumps ( diccionario)
#                self.clientsocket.send(pickledList)
        def broadcast_posicion(self,lista_ip,px,py,pz,ow,ox,oy,oz):
                    
    ##          Tipo de datos que contiene el tipo de mensaje, y su contenido
                diccionario = {"Tipo": "broadcast","Accion": "posicion","posicion":lista_ip,"px" : px,"py" : py,"pz" :pz,"ow":ow,"ox": ox,"oy": oy,"oz":oz}
                pickledList = pickle.dumps ( diccionario)
                self.clientsocket.send(pickledList)              
        
        def broadcast_orientacion(self,lista_ip,ow,ox,oy,oz):
                            
            ##          Tipo de datos que contiene el tipo de mensaje, y su contenido
                diccionario = {"Tipo": "broadcast","Accion": "orientacion","posicion":lista_ip,"ow":ow,"ox": ox,"oy": oy,"oz":oz}
                pickledList = pickle.dumps ( diccionario)
                self.clientsocket.send(pickledList)

            
        def broadcast_accion(self,lista_ip,accion):
#                print "Cliente broadcast_Accion"
            ##          Tipo de datos que contiene el tipo de mensaje, y su contenido
                diccionario = {"Tipo": "broadcast","Accion": "movimiento","posicion":lista_ip,"Tipo_accion":accion}
                pickledList = pickle.dumps ( diccionario)
                self.clientsocket.send(pickledList)


if __name__ == '__main__':

        cliente = Cliente()

