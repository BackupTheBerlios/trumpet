# UDP client example
import socket
import time
import threading
##import pickle
import pickle
import sys



lista_clientes = [5000]
mensaje = ""


 


class thread_recibir(threading.Thread):
    def __init__(self,s,lista):
        threading.Thread.__init__(self)
        self.socket = s
        self.lista = lista
    def run(self):
        while 1:
            
            data, address = self.socket.recvfrom(5000)
            mensaje = pickle.loads(data)
            if mensaje["Tipo"] == "cliente" :
                lista_clientes = mensaje["numero"]
                print "lista Clientes: ",lista_clientes
                
            elif mensaje["Tipo"] == "Mensaje" :
                print "Mensaje del servidor: ",mensaje["numero"]
                mensaje = mensaje["numero"]
                
            elif mensaje["Tipo"] == "broadcast" :
                print "Mensaje Broadcast: ",mensaje["numero"]
                mensaje = mensaje["numero"]
                
            elif mensaje["Tipo"] == "actualizar" :
                lista_clientes = mensaje["numero"]
                print "Mensaje Broadcast: ",lista_clientes               
                
            
            

                
if __name__ == '__main__':
    # Se establece la conexion
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto("Conexion", ("localhost",5000))
        lista = Clista_clientes(lista_clientes)
        recibir = thread_recibir(client_socket,lista)
        recibir.start()
        print"Escribe lista para ver una lista de todos los clientes conectados"
        print"Escribe mensaje para ver el mensaje actual que ha mandado el servidor"
        while 1:
    
                data = raw_input("> ")
                if data == "lista":
                    print lista_clientes
                if data == "mensaje":
                    print mensaje
                if data <> "q" and data <> "Q":
                    client_socket.sendto(data, ("localhost",5000))
                     
                else:
                        break
        client_socket.close()
    

##        enviar = thread_enviar(client_socket)
##        enviar.start()
