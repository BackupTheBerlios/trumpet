# /*
# SimpleScenes.cpp
# ---------------
# Code for the base scene class from which the specific scenes are derived
# */
import ogre.renderer.OGRE as ogre
import ogre.physics.OgreOde as OgreOde
import ogre.io.OIS as OIS
import clienteUDP 
import time

class CreatePlayer (OgreOde.CollisionListener, OgreOde.StepListener):
    KEY_DELAY = 1.0
    STEP_RATE = 0.01
    def __init__ ( self, world ,camera):
        global KEY_DELAY
        self.camera = camera
        OgreOde.CollisionListener.__init__(self)
        OgreOde.StepListener.__init__(self)
        self._world = world
        self._mgr = self._world.getSceneManager()
        self._world.setCollisionListener(self)
        self._space = self._world.getDefaultSpace()
        self._key_delay = 1.0 # KEY_DELAY
        self._last_node = 0
        self._delay = 0.0
        self._bodies=[] 
        self._geoms=[]
        self._joints=[]
        self._ragdollFactory = OgreOde.RagdollFactory()
        self.lista_personajes = []
        ogre.Root.getSingletonPtr().addMovableObjectFactory(self._ragdollFactory) 
        
        self.p = clienteUDP.conectar()  
        self.p.recibir.start()
        self.conjunto_nuevo = set([5000]) 
        self.conjunto_antiguo = set([5000])
        

        self._player = 0
        self.cliente_ip = 0
        self.ip_lista = 0
        self.lista_de_Ips = []
        self.tipoCamara = 1
        self.setInfoText("")
        self.cont = 0
        
        time.sleep(3)
     
        self.lista_clientes = self.p.getListaClientes()
        conjunto = set(self.lista_clientes)
        self._player = len(self.lista_clientes)-2
           
#        print "Los clientes actuales son",self.lista_clientes
#        print "El player es",self._player
        time.sleep(3)

        conjunto = set(self.lista_clientes)
        self.conjunto_antiguo = conjunto - self.conjunto_nuevo
        self.conjunto_nuevo = conjunto
#        print "conjunto antiguo ",self.conjunto_antiguo
#        print "conjunto nuevo ",self.conjunto_nuevo

        for ip in self.conjunto_antiguo:
                 #       #print "personaje creado numero ",self.cont
                        self.createPlayer(self.cont)
                        self.cont = self.cont + 1
        
    
        self.ip_lista = self._player
    # 
    # Called by OgreOde whenever a collision occurs, so 
    # that we can modify the contact parameters
    # 
    def collision( self, contact) :
#          "Simple Scenes Collision"
        ## Check for collisions between things that are connected and ignore them
        g1 = contact.getFirstGeometry()
        g2 = contact.getSecondGeometry()
    
        if (g1 and g2):
            b1 = g1.getBody()
            b2 = g2.getBody()
            if (b1 and b2 and OgreOde.Joint.areConnected(b1, b2)):
               return False 
    
        ## Set the friction at the contact
        ## Infinity didn't get exposed :(
        contact.setCoulombFriction( 9999999999 )    ### OgreOde.Utility.Infinity)
        contact.setBouncyness(0.1)
    
        ## Yes, this collision is valid
        return True


# /*
# Create a ragdoll
# */
    def createPlayer( self ,_num_personaje):
 
        self.tipoCamara = 0
        nombre_personaje = "personaje"+str(_num_personaje)
        nombre_model = "model"+str(_num_personaje)
        nombre_sight = "personaje_sight"+str(_num_personaje)
        nombre_camera = "personaje_camera"+str(_num_personaje)
        nombre_feet = "feet"+str(_num_personaje)
        nombre_torso = "torso"+str(_num_personaje)
        nombre_sound = "sound"+str(_num_personaje)
    
        personaje = self._mgr.createEntity(nombre_personaje,"FerPersonaje.mesh");
        personajeNode = self._mgr.getRootSceneNode().createChildSceneNode(nombre_personaje);
        modelNode = personajeNode.createChildSceneNode(nombre_model);
        modelNode.yaw(ogre.Math.DegreesToRadians(180))
        modelNode.attachObject(personaje);
        personajeNode.setScale(12,12,12);
        posicionActual = self.p.getPosicionActual(_num_personaje)
        personajeNode.setPosition(posicionActual["px"], posicionActual["py"], posicionActual["pz"])
        orientacionActual = self.p.getOrientacionActual(_num_personaje)
        personajeNode.setOrientation(orientacionActual["ow"],orientacionActual["ox"],orientacionActual["oy"],orientacionActual["oz"],)
#        personajeNode.setPosition(-61.5693, 240.5599, 3.27917)
    
        dollFeetBody = OgreOde.Body(self._world,nombre_feet)
        dollTorsoBody = OgreOde.Body(self._world,nombre_torso)  
        animationState = personaje.getAnimationState('Caminar')

        self.velocidad = 100
        self.delay = 1
        
        sightNode = modelNode.createChildSceneNode(nombre_sight,(0, -5, 5))
        cameraNode = modelNode.createChildSceneNode(nombre_camera)
        
        dollSpace = OgreOde.SimpleSpace(self._world,self._world.getDefaultSpace());
        dollSpace.setInternalCollisions(False)
        

        
        
        aab = modelNode.getAttachedObject(nombre_personaje).getBoundingBox(); 
        min = ogre.Vector3(aab.getMinimum().x*personajeNode.getScale().x,aab.getMinimum().y*personajeNode.getScale().y,aab.getMinimum().z*personajeNode.getScale().z)
        max = ogre.Vector3(aab.getMaximum().x*personajeNode.getScale().x,aab.getMaximum().y*personajeNode.getScale().y,aab.getMaximum().z*personajeNode.getScale().z);
        center = ogre.Vector3(aab.getCenter().x*personajeNode.getScale().x,aab.getCenter().y*personajeNode.getScale().y,aab.getCenter().z*personajeNode.getScale().z);
        size = ogre.Vector3(abs(max.x-min.x),abs(max.y-min.y),abs(max.z-min.z));
#        radius = (size.x>size.z)?size.z/2.0f:size.x/2.0f;
        if (size.x>size.z):
            radius = size.z/2.0
        else:
            radius = size.x/2.0
            


        

        ## Creamos una esfera la cual servira para desplazar al personaje
        dollFeetBody.setMass(OgreOde.SphereMass(70*2.5,radius))
        feetGeom = OgreOde.SphereGeometry(radius,self._world,None)
        feetTrans = OgreOde.TransformGeometry(self._world,dollSpace)
        modelNode.translate(ogre.Vector3(0,-radius/personajeNode.getScale().y,0))
        modelNode.translate(ogre.Vector3(0,11,0))
        feetTrans.setBody(dollFeetBody)
        feetTrans.setEncapsulatedGeometry(feetGeom)
        personajeNode.attachObject(dollFeetBody)     
        
        
        ## Keep track of the body
        self._bodies.append(dollFeetBody)
        self._geoms.append(feetGeom)
        self._geoms.append(feetTrans)


#        creamos una capsula que envolvera el resto del cuerpo                                  
        dollTorsoBody.setAffectedByGravity(False)
        dollTorsoBody.setDamping(0,50000)
        dollTorsoBody.setMass(OgreOde.CapsuleMass(70*2.5,radius,(0,1,0),radius))
        torsoTrans = OgreOde.TransformGeometry(self._world,dollSpace)
        torsoGeom = OgreOde.CapsuleGeometry(radius,size.y-4*radius,self._world,None)
        torsoGeom.setPosition(ogre.Vector3(0,size.y-((size.y-4*radius)/2+2*radius),0))
        torsoGeom.setOrientation(ogre.Quaternion(ogre.Degree(90),(1,0,0)))
        torsoTrans.setBody(dollTorsoBody)
        torsoTrans.setEncapsulatedGeometry(torsoGeom)
        personajeNode.attachObject(dollTorsoBody)        

    
        ## Keep track of the body
        self._bodies.append(dollTorsoBody)
        self._geoms.append(torsoGeom)
        self._geoms.append(torsoTrans)
        
        joint = OgreOde.HingeJoint(self._world)
        joint.attach(dollTorsoBody,dollFeetBody)
        joint.setAxis((1,0,0))
        self._joints.append(joint)

    

        registro_personajes = {"personaje_entity" : personaje,
                                    "personaje_node" : personajeNode,
                                    "model_node" : modelNode,
                                    "sight_node" : sightNode,
                                    "camera_node" : cameraNode,
                                    "dollFeetBody" : dollFeetBody,
                                    "dollTorsoBody" : dollTorsoBody,
                                    #"sonido" : sound,
                                    "dollSpace" : dollSpace,
                                    "animacion" : animationState
                                    }
        self.lista_personajes.append(registro_personajes)
        
        
   
  
        
        
        

    def camaraLibre(self):
        self.camera.setPosition((personajeNode.getPosition().x,40,personajeNode.getPosition().z+100))
 ## we need to register the framelistener
    def camara3Persona(self):
#        Cambiar para acercar o alejar la camara, 
        followFactor = 0.3
#        Altura de la camara
        camHeight = 140.0
#        Distancia de la camara al objetivo
        camDistance = -260.0
#        Posicion a la que apunta la camara
        camLookAhead = -450
        
    
        
        q = self.lista_personajes[self._player]["personaje_node"].getOrientation()
        toCam = self.lista_personajes[self._player]["personaje_node"].getPosition()
    
        toCam.y += camHeight
        toCam.z -= camDistance * q.zAxis().z
        toCam.x -= camDistance * q.zAxis().x
            
            
    
        self.camera.move( (toCam - self.camera.getPosition()) * followFactor )
        self.camera.lookAt(self.lista_personajes[self._player]["personaje_node"].getPosition() + ((self.lista_personajes[self._player]["personaje_node"].getOrientation() * ogre.Vector3().UNIT_Z) * camLookAhead))

    def frameStarted(self,frameEvent,time,accion):
         

      
        if(accion=="up"):
                 px = self.lista_personajes[self._player]["personaje_node"].getPosition().x
                 py = self.lista_personajes[self._player]["personaje_node"].getPosition().y
                 pz = self.lista_personajes[self._player]["personaje_node"].getPosition().z
                 ow = self.lista_personajes[self._player]["personaje_node"].getOrientation().w
                 ox = self.lista_personajes[self._player]["personaje_node"].getOrientation().x
                 oy = self.lista_personajes[self._player]["personaje_node"].getOrientation().y
                 oz = self.lista_personajes[self._player]["personaje_node"].getOrientation().z
                 self.p.broadcast_posicion(self.ip_lista,px,py,pz)  
                 self.p.broadcast_orientacion(self.ip_lista,ow,ox,oy,oz)
                 self.p.broadcast_accion(self.ip_lista,accion)
        if (accion=="down"):
                 px = self.lista_personajes[self._player]["personaje_node"].getPosition().x
                 py = self.lista_personajes[self._player]["personaje_node"].getPosition().y
                 pz = self.lista_personajes[self._player]["personaje_node"].getPosition().z
                 ow = self.lista_personajes[self._player]["personaje_node"].getOrientation().w
                 ox = self.lista_personajes[self._player]["personaje_node"].getOrientation().x
                 oy = self.lista_personajes[self._player]["personaje_node"].getOrientation().y
                 oz = self.lista_personajes[self._player]["personaje_node"].getOrientation().z
                 self.p.broadcast_posicion(self.ip_lista,px,py,pz)  
                 self.p.broadcast_orientacion(self.ip_lista,ow,ox,oy,oz)
                 self.p.broadcast_accion(self.ip_lista,accion)
                 
        if (accion=="right" or accion=="left"):
                 px = self.lista_personajes[self._player]["personaje_node"].getPosition().x
                 py = self.lista_personajes[self._player]["personaje_node"].getPosition().y
                 pz = self.lista_personajes[self._player]["personaje_node"].getPosition().z
                 ow = self.lista_personajes[self._player]["personaje_node"].getOrientation().w
                 ox = self.lista_personajes[self._player]["personaje_node"].getOrientation().x
                 oy = self.lista_personajes[self._player]["personaje_node"].getOrientation().y
                 oz = self.lista_personajes[self._player]["personaje_node"].getOrientation().z
                 self.p.broadcast_posicion(self.ip_lista,px,py,pz)  
                 self.p.broadcast_orientacion(self.ip_lista,ow,ox,oy,oz)
                 self.p.broadcast_accion(self.ip_lista,accion)
            
        if (accion=="accionF4"):
               # #print self.p.getListaMov()
    
                self._delay = 0.0

#        if (accion=="accionF3"):
#
#                lista_clientes = self.p.getListaClientes()
#                conjunto = set(lista_clientes)
#                self._player = len(lista_clientes)-2
#           
#                print "Los clientes actuales son",lista_clientes
#                print "El player es",self._player
#    
#                self._delay = 0.0
#            
        if (accion=="accionF2"):
                ##print "F2"
#        if(self.lista_clientes < self.p.getListaClientes()):
                self.lista_clientes = self.p.getListaClientes()
                conjunto = set(self.lista_clientes)
                self.conjunto_antiguo = conjunto - self.conjunto_nuevo
                self.conjunto_nuevo = conjunto
#                print "conjunto antiguo ",self.conjunto_antiguo
#                print "conjunto nuevo ",self.conjunto_nuevo

                for ip in self.conjunto_antiguo:
                 #       #print "personaje creado numero ",self.cont
                        self.createPlayer(self.cont)
                        self.cont = self.cont + 1
                ##print "player actual ",self._player
               # #print"lista de player ",lista_clientes
                self._delay = 0.0
#    
#        self.ip_lista = self._player

        if (accion=="camara0"):
  
            self.tipoCamara = 0
            
        if (accion=="camara1"):
            self.tipoCamara = 1
        
        if (self.tipoCamara == 0):
            self.camara3Persona()



    def frameEnded(self,frameEvent,time,accion):
        
            _personaje_thrust = 0;
            _personaje_rotate = 0;
            cont = 0
            for i in self.lista_personajes:
                                    _personaje_thrust = 0;
                                    _personaje_rotate = 0;
                #if(cont<>self._player):
                    
                                    if(self.p.getListaMovimientos(cont)<>[]):
                                        var_mov = self.p.getMovimiento(cont)
                                    else : 
                                        var_mov = "null"                               
                                        _personaje_rotate = 0;
                                    if (var_mov=="left"):
                                        #print "left"
                                        _personaje_rotate += -1;

                                     
                                    if (var_mov=="right"):
                                        #print "right"
                                        _personaje_rotate += 1;
                                    
                                    if (var_mov=="up"):
                                        #print "up"
                                        _personaje_thrust += -1;
                                        self.lista_personajes[cont]["animacion"].setLoop(True)
                                        self.lista_personajes[cont]["animacion"].setEnabled(True)
                                        self.lista_personajes[cont]["animacion"].addTime(0.05)
                                        self.sonidoCaminar = True
                               #                  self.lista_personajes[_num_personaje]["animacion"].setLoop(True)
                                     
                                    if (var_mov=="down"):
                                         #print "down"
                                         _personaje_thrust += 1; 
                                         self.lista_personajes[cont]["animacion"].setLoop(True)
                                         self.lista_personajes[cont]["animacion"].setEnabled(True)
                                         self.lista_personajes[cont]["animacion"].addTime(2.7)
                                         self.sonidoCaminar = True
                     #                  self.lista_personajes[_num_personaje]["animacion"].setLoop(True)
                        #             self.sonidoCaminar = False
                                
                                    if (_personaje_rotate == 0):
                                    
                                        self.lista_personajes[cont]["dollFeetBody"].wake();
                                        self.lista_personajes[cont]["dollFeetBody"].setAngularVelocity(ogre.Vector3(self.lista_personajes[cont]["dollFeetBody"].getAngularVelocity().x,0,0));
                                    
                                    else:
                                    
                                        self.lista_personajes[cont]["dollFeetBody"].wake();
                                        q1 = self.lista_personajes[cont]["dollTorsoBody"].getOrientation();
                                        q2 = ogre.Quaternion(ogre.Degree(-4*_personaje_rotate),(0,1,0));
                                        self.lista_personajes[cont]["dollTorsoBody"].setOrientation(q1*q2);
                                    
                                 
                                    if (_personaje_thrust == 0):
                                    
                                        self.lista_personajes[cont]["dollFeetBody"].wake();
                                        self.lista_personajes[cont]["dollFeetBody"].setLinearVelocity(ogre.Vector3(0,self.lista_personajes[cont]["dollFeetBody"].getLinearVelocity().y,0));
                                        self.lista_personajes[cont]["dollFeetBody"].setAngularVelocity(ogre.Vector3(0,self.lista_personajes[cont]["dollFeetBody"].getAngularVelocity().y,0));
                        
                                    
                                    else:
                                    
                                        speed = self.velocidad;
                                        self.lista_personajes[cont]["dollFeetBody"].wake();
                                        q = self.lista_personajes[cont]["dollTorsoBody"].getOrientation();
                                        self.lista_personajes[cont]["dollFeetBody"].setAngularVelocity(q*ogre.Vector3(speed*_personaje_thrust*ogre.Math.Cos(1.0),self.lista_personajes[cont]["dollFeetBody"].getAngularVelocity().y,0));
                                    
                                 
                                    q = self.lista_personajes[cont]["dollTorsoBody"].getOrientation();         
                                    x = q.xAxis();
                                    y = q.yAxis();
                                    z = q.zAxis();
                                    self.lista_personajes[cont]["dollTorsoBody"].wake();
                                    self.lista_personajes[cont]["dollTorsoBody"].setOrientation(ogre.Quaternion(x,(0,1,0),z));
                                    self.lista_personajes[cont]["dollTorsoBody"].setAngularVelocity(ogre.Vector3(0,0,0)); 
             
                                    cont = cont + 1


    # 
    # Utility method to set the information string in the UI
    # 
    def setInfoText(self,  text):
#         #print "Setinfotext"
        ogre.OverlayManager.getSingleton().getOverlayElement("OgreOdeDemos/Info").setCaption(ogre.UTFString("Info: " + text))

    def getLastNode(self):
#         #print "getlastnode"
        return self._last_node
        
    ## If we register this with a stepper it'll get told every time the world's about to be stepped
    def preStep(self, time):
#         #print "preStep"
        self.addForcesAndTorques()
        return True
        
    def addForcesAndTorques(self):
#         #print "Addforces"
        pass

        
        
  # 
    # Destructor, delete everything we're keeping track of
    # 
    def __del__ ( self ):
        ## Stop listening for collisions
        if (self._world.getCollisionListener() == self): 
            self._world.setCollisionListener(None)
    
        ## Delete all the joints
        for i in self._joints:
            del (i)
        clearList = []
        ## Run through the list of bodies we're monitoring
        for i in self._bodies:
            ## Get the SCENE node this body controls
            node = i.getParentSceneNode()
            if (node):
                ## Get its name and remember all the things attached to it
                name = node.getName()
                num = node.numAttachedObjects()
                for cur in range ( num ) :
                    obj = node.getAttachedObject(cur)
                    if (obj.getMovableType() != "OgreOde::Body"):
                        clearList.append(obj)
    
                ## Destroy the node by name
                
                self._mgr.getRootSceneNode().removeAndDestroyChild(name)
            ## Delete the body
            del (i)
    
        ## Remove all the entities we found attached to scene nodes we're controlling
        for i in clearList:
            if (i.getMovableType() == "Entity") :
                self._mgr.destroyMovableObject(i)
            elif (i.getMovableType() == "ParticleSystem")  :
                self._mgr.destroyParticleSystem(i)
    
        ## Delete all the collision geometries
        for i in self._geoms:
            del (i)
        ## Remove all the entities we found attached to scene nodes we're controlling
        for i in self.lista_personajes:
# #             assert (i.getParentNode ())
# #             assert (i.getParentNode ().getParent())
            self._mgr.getRootSceneNode().removeAndDestroyChild(i.getParentNode().getName ())
            self._mgr.destroyMovableObject(i.getName(), OgreOde.RagdollFactory.FACTORY_TYPE_NAME)
        ogre.Root.getSingletonPtr().removeMovableObjectFactory(self._ragdollFactory)
        del self._ragdollFactory 
