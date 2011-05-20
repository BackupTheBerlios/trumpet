import socket
from threading import Thread
import pickle

lista_clientes = []
lista_ip_clientes = []
lista_posiciones = []
lista_orientacion = []
lista_movimientos = [[]]
lista_ultimo_mov=["null"]
#Clase con el hilo para atender a los clientes.
#En el constructor recibe el socket con el cliente y los datos del
#cliente para escribir por pantalla
class Cliente(Thread):
    def __init__(self, socket_cliente, datos_cliente):
        Thread.__init__(self)
        self.socket = socket_cliente
        self.datos = datos_cliente
 
    # Bucle para atender al cliente.       
    def run(self):
      global lista_clientes
      global lista_posiciones
      global lista_orientacion
      global lista_movimientos
      global lista_ultimo_mov
      global mensaje_servidor
      global mensaje
      # Bucle indefinido hasta que el cliente envie "adios"
      seguir = True
      while 1:
         # Espera por datos
         peticion = self.socket.recv(1000)

         mensaje = pickle.loads (peticion)
         if mensaje["Tipo"] == "broadcast":
#                print "Server primero broadcast"
#                if mensaje["Accion"]=="posicion":
##                    print "Server broadcast posicion"
#
#                    diccionario_posiciones = {"px": mensaje["px"],"py": mensaje["py"],"pz": mensaje["pz"]}
#                    lista_posiciones[mensaje["posicion"]]=diccionario_posiciones
#                    for i in lista_clientes:
#                    
#     ######          Tipo de datos que contiene el tipo de mensaje, y su conten      
#             ##          Tipo de datos que contiene el tipo de mensaje, y su contenido
#                         diccionario = {"Tipo": "actualizar_lista_posiciones","lista_posiciones":lista_posiciones}
#     #                    print "Lista posiciones: ",lista_posiciones
#                         pickledList = pickle.dumps ( diccionario)
#                         i.send(pickledList)

                if mensaje["Accion"]=="posicion":
#                    print "Server broadcast posicion"
                    diccionario_posiciones = {"px": mensaje["px"],"py": mensaje["py"],"pz": mensaje["pz"]}
                    lista_posiciones[mensaje["posicion"]]=diccionario_posiciones
                    diccionario_orientacion = {"ow": mensaje["ow"],"ox": mensaje["ox"],"oy": mensaje["oy"],"oz": mensaje["oz"]}
                    lista_orientacion[mensaje["posicion"]]=diccionario_orientacion
                    for i in lista_clientes:

                         diccionario = {"Tipo": "actualizar_lista_posiciones","lista_posiciones":lista_posiciones,"lista_orientacion":lista_orientacion}
     #                    print "Lista posiciones: ",lista_posiciones
                         pickledList = pickle.dumps ( diccionario)
                         i.send(pickledList)
                         
                    
                if mensaje["Accion"]=="orientacion":
#                    print "Server broadcast orientacion"

                    diccionario_orientacion = {"ow": mensaje["ow"],"ox": mensaje["ox"],"oy": mensaje["oy"],"oz": mensaje["oz"]}
                    lista_orientacion[mensaje["posicion"]]=diccionario_orientacion
                    for i in lista_clientes:
                                 ##          Tipo de datos que contiene el tipo de mensaje, y su contenido
                         diccionario = {"Tipo": "actualizar_lista_orientacion","lista_orientacion":lista_orientacion}
     #                    print "Lista posiciones: ",lista_orientacion
                         pickledList = pickle.dumps ( diccionario)
                         i.send(pickledList)
                    
                if mensaje["Accion"]=="movimiento":
#                                   print "Server despues accion_broadcast"
                    lista = []
                    lista.insert(0, mensaje["Tipo_accion"])
                    lista_movimientos[mensaje["posicion"]]=lista
                    for i in lista_clientes:                               ##          Tipo de datos que contiene el tipo de mensaje, y su contenido
                         diccionario = {"Tipo": "actualizar_lista_movimientos","lista_movimientos":lista_movimientos}
##                         print "Server Al final manda lista Movimientos: ",lista_orientacion
                         pickledList = pickle.dumps ( diccionario)
                         i.send(pickledList)
                
                
#                                   lista_ultimo_mov[mensaje["posicion"]]= mensaje["Tipo_accion"]
#                                   print lista_ultimo_mov
###                                   lista.append(mensaje["Tipo_accion"])
#                                   
#                                   for i in lista_clientes:                               ##          Tipo de datos que contiene el tipo de mensaje, y su contenido
#                                        diccionario = {"Tipo": "actualizar_lista_movimientos","lista_movimientos":lista_ultimo_mov}
#               #                         print "Server Al final manda lista Movimientos: ",lista_orientacion
#                                        pickledList = pickle.dumps ( diccionario)
#                                        i.send(pickledList)


                    
                    

#         print "Ha llegado mensaje"
#         print peticion
##         self.socket.send("Te contesto")
          # Contestacion a "hola"
         if ("hola"==peticion):
#             print str(self.datos)+ " envia hola: contesto"
             self.socket.send("pues hola")
             
         # Contestacion y cierre a "adios"
         if ("adios"==peticion):
#             print str(self.datos)+ " envia adios: contesto y desconecto"
             self.socket.send("pues adios")
             self.socket.close()
#             print "desconectado "+str(self.datos)
             seguir = False
        
class enviar(Thread):

    def __init__(self, socket_cliente, datos_cliente):
        Thread.__init__(self)
        self.socket = socket_cliente
        self.datos = datos_cliente
 
    # Bucle para atender al cliente.       
    def run(self):
         
      global lista_clientes
      global lista_posiciones
      global lista_orientacion
      global lista_movimientos
      global lista_ultimo_mov
      global mensaje_servidor
      global mensaje

      while True:
        data = raw_input(">")
        if(data == "broadcast"):
            for i in lista_clientes:
                pickledList = pickle.dumps ( data)
                i.send(pickledList)

        elif data == "privado":
##          Si no es broadcast, manda un mensaje a un cliente determinado 
#            print "Lista de clientes del servidor: ",lista_clientes
            dir_cliente = raw_input("Introduce el cliente >")
            mensaje = raw_input("Introduce el mensaje >")
            diccionario = {"Tipo": "Mensaje", "numero": mensaje}
            server_socket.sendto(diccionario, ("localhost",int(dir_cliente)))
                 

            



if __name__ == '__main__':
   global lista_clientes
   global lista_posiciones
   global lista_orientacion
   global lista_movimientos
   global lista_ultimo_mov
   global mensaje_servidor
   global mensaje
              
   # Se prepara el servidor
   server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   server.bind(("", 4443))
   server.listen(1)
   print "Esperando clientes..."
##   global lista_clientes
##   global lista_socket_clientes
   # bucle para atender clientes
   while 1:
     
      # Se espera a un cliente
      socket_cliente, datos_cliente = server.accept()
      
      lista_clientes.append(socket_cliente)
      lista_ip_clientes.append(datos_cliente[1])
      lista_posiciones.append({"px": -61.5693,"py": 240.5599,"pz": 3.27917})
      lista_orientacion.append({"ow":0,"ox":1,"oy": 0,"oz": 1})
      lista_movimientos.append([])
      lista_ultimo_mov.append('null')
      cont = 0
      for i in lista_ip_clientes:
          lista_movimientos[cont]=[]
          lista_ultimo_mov[cont]="null"
          cont = cont+1

##                diccionario = {"Tipo": "cliente", "numero": address[1]}
      for i in lista_clientes:
######          Tipo de datos que contiene el tipo de mensaje, y su contenido
            diccionario = {"Tipo": "actualizar_lista_clientes", "lista_clientes": lista_ip_clientes}
            print "Lista clientes del servidor: ",lista_clientes
            pickledList = pickle.dumps ( diccionario)
            i.send(pickledList)
                   
##          Tipo de datos que contiene el tipo de mensaje, y su contenido
            diccionario = {"Tipo": "actualizar_lista_posiciones","lista_posiciones":lista_posiciones,"lista_orientacion":lista_orientacion}
            print "Lista posiciones: ",lista_posiciones
            pickledList = pickle.dumps ( diccionario)
            i.send(pickledList)
            
            
                    ##          Tipo de datos que contiene el tipo de mensaje, y su contenido
#            diccionario = {"Tipo": "actualizar_lista_orientacion","lista_orientacion":lista_orientacion}
#            print "Lista posiciones: ",lista_orientacion
#            pickledList = pickle.dumps ( diccionario)
#            i.send(pickledList)
            
                                            ##          Tipo de datos que contiene el tipo de mensaje, y su contenido
            diccionario = {"Tipo": "actualizar_lista_movimientos","lista_movimientos":lista_movimientos}
#            diccionario = {"Tipo": "actualizar_lista_movimientos","lista_movimientos":lista_ultimo_mov}

#            print "Lista posiciones: ",lista_orientacion
            pickledList = pickle.dumps ( diccionario)
            i.send(pickledList)
      # Se escribe su informacion
      print "conectado "+str(datos_cliente)
      
      # Se crea la clase con el hilo y se arranca.
      hilo = Cliente(socket_cliente, datos_cliente)
      hilo.start()
      hilo2 = enviar(socket_cliente, datos_cliente)
      hilo2.start()
