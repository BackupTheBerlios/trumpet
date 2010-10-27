
#=======================================================================================
# #Prototipo
# El vehiculo choca contra las paredes y otros objetos que hay en el escenario
# Hay una camara en 3 persona, y otra con la cual se ve una vista aerea
# Muestra informacion en la pantalla
# Las teclas para controlar el movimiento son:
# - teclas de direccion para el movimiento del coche
# - 1 = camara 3 persona, 2= camara aerea
# - Espacio = cambia el tipo de sombra 
# - N = cambia el tipo de vehiculo
# - E = muestra los bounding Box
# - X = cambia la traccion del vehiculo
# - P = pausa el juego
# Se ha puesto una condicion, para que al pulsar una tecla solo recoja la accion una vez,
# de este modo, solo recoge una tecla por segundo
#
#Cosas que faltan :
#-Personaje humano
#-Ajusta la pantalla de informacion
#-Asegurarse que el sceneManager es interior
#========================================================================================




import sys
sys.path.insert(0,'..')
import PythonOgreConfig

import ogre.renderer.OGRE as ogre
import ogre.physics.OgreOde as OgreOde
import ogre.io.OIS as OIS
import SampleFramework as sf


STEP_RATE=0.01
ANY_QUERY_MASK                  = 1<<0
STATIC_GEOMETRY_QUERY_MASK      = 1<<4


carNames = [
    "Subaru",
    "Jeep",
    "JeepSway"
]
carFileNames= [
    "subaru.ogreode",
    "jeep.ogreode",
    "jeep.ogreode"
]
sSelectedCar = 1
maxNumCar = 3

      


class PrototipoApplication(sf.Application):
    def __init__ ( self ):
        sf.Application.__init__(self)

        self.plane = 0
        self.stepper = 0   
        self.world = 0
        self.delay=0.0
        self.spot=None
        self.time_elapsed = 0.0
        self.time_step = 0.1 ## SimpleScenes::STEP_RATE
        self.looking = self._chasing = False
        self.paused = False
        self.bodies=[]  # an array to keep objects around in (like c++ "new" )
        self.geoms=[]
        self.joints=[]



        
    def _createScene(self):
        global STEP_RATE, ANY_QUERY_MASK, STATIC_GEOMETRY_QUERY_MASK
        sceneManager = self.sceneManager
        ogre.MovableObject.setDefaultQueryFlags (ANY_QUERY_MASK)
        self.shadowtype=0
        ## Set up shadowing
        sceneManager.setShadowTechnique(ogre.SHADOWTYPE_TEXTURE_MODULATIVE)
        sceneManager.setShadowColour((0.5, 0.5, 0.5))
        sceneManager.setShadowFarDistance(30)
    
        if self.root.getRenderSystem().getName().startswith ('direct'): 
            sceneManager.setShadowTextureSettings(1024, 2)
        else: 
            sceneManager.setShadowTextureSettings(512, 2)
    
        ## Add some default lighting to the scene
        sceneManager.setAmbientLight( (.25, .25, .25) )
        light = sceneManager.createLight('MainLight')
        light.setPosition (0, 0, 1)
        light.CastShadows=True
    
        ## Create a directional light to shadow and light the bodies
        self.spot = sceneManager.createLight("Spot")
        self.spot.setType(ogre.Light.LT_DIRECTIONAL)
        self.spot.setDirection(-0.40824828,-0.81649655,-0.40824828)
        self.spot.setCastShadows(True)
        self.spot.setSpecularColour(1,1,0.8)

        ## Give us some sky
        sceneManager.setSkyBox(True,"kk3d/DesertVII", 5000, True) # Examples/SpaceSkyBox",5000,True)
    
        ## Position and orient the camera
        self.camera.setPosition(13,4.5,0)
        self.camera.lookAt(0,0.5,0)
        self.camera.setNearClipDistance(0.5)

        ## Create the ODE world
        self.world = OgreOde.World(sceneManager)
        self.world.setGravity( (0,-9.80665,0) )
        self.world.setCFM(0.0000010 )  # 10e-5)
        self.world.setERP(0.8)
        self.world.setAutoSleep(True)
        self.world.setAutoSleepAverageSamplesCount(10)
        self.world.setContactCorrectionVelocity(1.0)
        #Para importar objetos
        self.dotOgreOdeLoader = OgreOde.DotLoader(self.world)
        
        ## Create something that will step the world, but don't do it automatically
        stepper_mode_choice = 2
        stepper_choice = 3
        time_scale = 1.7
        max_frame_time = 1.0 / 4.0
        frame_rate = 1.0 / 60.0


        if stepper_mode_choice ==0:    stepModeType = OgreOde.StepHandler.BasicStep
        elif stepper_mode_choice ==1:  stepModeType = OgreOde.StepHandler.FastStep
        elif stepper_mode_choice ==2:  stepModeType = OgreOde.StepHandler.QuickStep
        else: stepModeType = OgreOde.StepHandler.QuickStep

        if stepper_choice == 0:
            self.stepper = OgreOde.StepHandler(self.world, StepHandler.QuickStep, 
                STEP_RATE, max_frame_time,  time_scale)
        elif stepper_choice == 1:
           self.stepper =  OgreOde.ExactVariableStepHandler(self.world, 
                stepModeType, 
                STEP_RATE,
                max_frame_time,
                time_scale)
        
        elif stepper_choice == 2:
            self.stepper = OgreOde.ForwardFixedStepHandler(self.world, 
                stepModeType, 
                STEP_RATE,
                max_frame_time,
                time_scale)
        else:
            self.stepper = OgreOde.ForwardFixedInterpolatedStepHandler (self.world, 
                stepModeType, 
                STEP_RATE,
                frame_rate,
                max_frame_time,
                time_scale)
 
        ##_stepper.setAutomatic(OgreOde.StepHandler.AutoMode_PostFrame, mRoot)
        ##_stepper.setAutomatic(OgreOde.Stepper.AutoMode_PreFrame, mRoot)

    
        self.root.getSingleton().setFrameSmoothingPeriod(5.0)
        ##Root.getSingleton().setFrameSmoothingPeriod(0.0)
    
        ## Create a default plane to act as the ground
        self.plane = OgreOde.InfinitePlaneGeometry(ogre.Plane(ogre.Vector3(0,1,0),0),self.world, self.world.getDefaultSpace())
        s = sceneManager.createStaticGeometry("StaticFloor")
        s.setRegionDimensions((160.0, 100.0, 160.0))
        ## Set the region origin so the center is at 0 world
        s.setOrigin(ogre.Vector3().ZERO)
    
        ## Use a load of meshes to represent the floor
        i = 0
        for z in range (-80, 80, 20 ):
            for x in range (-80, 80, 20):
                name = "Plane_" + str(i)
                i += 1
                
                entity = sceneManager.createEntity(name, "plane.mesh")
                entity.setQueryFlags (STATIC_GEOMETRY_QUERY_MASK)
                entity.setUserObject(self.plane)
                entity.setCastShadows(False)
                s.addEntity(entity, ogre.Vector3(x,0,z))
        s.build()    
        ## Load up our UI and display it
        pOver = ogre.OverlayManager.getSingleton().getByName("OgreOdeDemos/Overlay")    
        pOver.show()
    

        
        
        #=======================================================================
        # Piso
        #=======================================================================
        self.create_ODE_Terrain("primerPiso.mesh",(70,0,70),ogre.Vector3(1,1,1));
        #===============================================================================
        # Objeto en mitad del escenario
        #===============================================================================

#        crea un objeto con los atributos: nombre de la entida, malla que queremos, nodo,body,tamano,posicion
        self._createObjectos("crate","Barrel.mesh","nodoBarril","bodyBarril",(5.31985, 6.11992, 5.31985),(12,80,12))
        self._createObjectos("crate2","Barrel.mesh","nodoBarril2","bodyBarril2",(5.31985, 6.11992, 5.31985),(8,50,8))
        self._createObjectos("crate3","Barrel.mesh","nodoBarril3","bodyBarril3",(5.31985, 6.11992, 5.31985),(0,60,0))
        

        
        #=======================================================================
        # Muestra la informacion en la pantalla
        #=======================================================================
        self._createInformacion()
        
        
        
        
    

        
        
        # Carga la informacion en la pantalla
    def _createInformacion(self):
            
        pOver = ogre.OverlayManager.getSingleton().getByName("OgreOdeDemos/Overlay")
        ogre.OverlayManager.getSingleton().getOverlayElement("OgreOdeDemos/Name").setCaption("Nombre: "+ "Prototipo")
        ogre.OverlayManager.getSingleton().getOverlayElement("OgreOdeDemos/Keys").setCaption("Teclas: " + "UP/DOWN - Acelerar/Frenar, <-/-> - Girar, X - Cambiar traccion, N - Cambiar coche")
        ogre.OverlayManager.getSingleton().getOverlayElement("OgreOdeDemos/OtherKeys").setCaption("Extra: " + "E - Debug mode")
        pOver.show()
        
        
    def _createObjectos(self,nombre,malla,nodo,body,tamano,posicion):
        
            ent = self.sceneManager.createEntity(nombre,malla)
            ent.setQueryFlags(1<<2)
            node = self.sceneManager.getRootSceneNode().createChildSceneNode(nombre)
            node.attachObject(ent)
    ##        ent.setNormaliseNormals(True)
            ent.setCastShadows(True)
    
            body = OgreOde.Body(self.world)
            self.bodies.append( body )
    
            size = tamano
    
            mass = OgreOde.BoxMass(0.5,size)
            #mass.setDensity(0.01,size)
            geom = OgreOde.BoxGeometry(size,self.world,self.world.getDefaultSpace())
            self.geoms.append( geom )
            body.setMass(mass)
    
    ###    Une el nodo y el body
            node.attachObject(body)
            geom.setBody(body)
    #        #node.setScale(size)
            ent.setUserObject(geom)
    
    
            body.setPosition(posicion)
       
        
        
##     // Create the tri-mesh terrain from a mesh
    def create_ODE_Terrain(self,meshFile,position,size ):
         
         sn = self.sceneManager.getRootSceneNode().createChildSceneNode("TerrainNode",position);
         ent = self.sceneManager.createEntity("Terrain",meshFile);
         sn.attachObject(ent);
         sn.setScale(size);
 
         ei = OgreOde.EntityInformer(ent,sn._getFullTransform());
         self.terrainTriMeshGeom = ei.createStaticTriangleMesh(self.world,self.world.getDefaultSpace());
         

            
        
# 
# The frame listener will notify us when a frame's 
# about to be started, so we can update stuff
# 
    def frameStarted (self, evt, Keyboard, Mouse):
        ## Set the shadow distance according to how far we are from the plane that receives them
        self.sceneManager.setShadowFarDistance((abs(self.camera.getPosition().y) + 1.0) * 3.0)
  

           

                
#    ## we need to register the framelistener
    def _createFrameListener(self):
        ## note we pass ourselves as the demo to the framelistener
        self.frameListener = CollisionFrameListener(self, self.renderWindow, self.camera,self.world,self.stepper)
        self.root.addFrameListener(self.frameListener)
        ##Listener para cambiar las opciones de pantalla
        self.frameListenerOpciones = OpcionesFrameListener(self.renderWindow,
            self.camera,
            self.sceneManager,
            self.stepper,
            self.root,
            self.world)
        self.root.addFrameListener(self.frameListenerOpciones)
        self.frameListenerOpciones.showDebugOverlay(True)
        ##Listener para manejar el vehiculo
        self.frameListenerVehiculo = VehiculoFrameListener(self,self.renderWindow,self.camera,self.dotOgreOdeLoader)
        self.root.addFrameListener(self.frameListenerVehiculo)
  
  
  
#===============================================================================
# listener que trata las colisiones        
#===============================================================================
class CollisionFrameListener ( sf.FrameListener,OgreOde.CollisionListener ):
    def __init__( self, demo, renderWindow, camera,world,stepper ):
        sf.FrameListener.__init__(self, renderWindow, camera)
        OgreOde.CollisionListener.__init__(self)
        
        self.world = world
        self.stepper = stepper
        
        self.world.setCollisionListener(self)
       
             
    def frameStarted(self, frameEvent):
        #time = 1.0/60.0
        if self.stepper.step(frameEvent.timeSinceLastFrame):
            self.world.synchronise()
           
        return sf.FrameListener.frameStarted(self, frameEvent)
#    # The frame listener is informed after every frame
#    # 
#    def frameEnded(self, evt):
        
    def collision( self, contact) :
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
    
    
        
#===============================================================================
# Frame listener que trata las opciones de visualizacion como son el tipo de sombras, 
# ver debug mode y poner en pausa la aplicacion        
#===============================================================================
class OpcionesFrameListener(sf.FrameListener):
 
 
    def __init__(self, renderWindow, camera, sceneManager,stepper,root,world):
        # Subclass any Python-Ogre class and you must call its constructor.
        sf.FrameListener.__init__(self, renderWindow, camera)
        self.sceneManager = sceneManager
        self.stepper = stepper
        self.root = root
        self.world = world
        self.test = 0
        self.delay = 1.0
        self.shadowtype = 0
        self.keepRendering = True
        self.paused = False

 
        
    def _setupInput(self):
        # Initialize OIS.
        windowHnd = self.renderWindow.getCustomAttributeInt("WINDOW")
        self.InputManager = OIS.createPythonInputSystem([("WINDOW", str(windowHnd))])
 
        # Create all devices, only catch joystick exceptions since most people use Key/Mouse.
        self.Keyboard = self.InputManager.createInputObjectKeyboard(OIS.OISKeyboard, self.bufferedKeys)
        self.Mouse = self.InputManager.createInputObjectMouse(OIS.OISMouse, self.bufferedMouse)
        try:
            self.Joy = self.InputManager.createInputObjectJoyStick(OIS.OISJoyStick, self.bufferedJoy)
        except:
            self.Joy = False
 
        #Set initial mouse clipping size.
#        self.windowResized(self.renderWindow)
 
        # Register as a Window listener.
        ogre.WindowEventUtilities.addWindowEventListener(self.renderWindow, self);
        
    def frameStarted(self, frameEvent):
        if(self.renderWindow.isClosed()):
            return False
 
        # Capture and update each device, this will also trigger any listeners.
        self.Keyboard.capture()
#        self.Mouse.capture()

    
        if self.Keyboard.isKeyDown(OIS.KC_1):
            print "1"
            
        # Process unbuffered key input.
#        if not self.keyPressed(frameEvent):
#            return False
#        self.keyReleased(frameEvent)
 
        return self.keepRendering
    
# /*
# The frame listener will let us know when a frame's ended. So we
# can do stuff that we can't do in a frame started event
# e.g. delete things that we can't delete at the start of a frame,
# presumably because some processing has already been done, leaving
# things dangling, like particle systems.
# */
    def frameEnded(self, frameEvent):
        if(self.renderWindow.isClosed()):
            return False
 
        # Capture and update each device, this will also trigger any listeners.
        self.Keyboard.capture()
#        self.Mouse.capture()



#        ## Step the world and then synchronise the scene nodes with it, 
#        ## we could get this to do this automatically, but we 
#        ## can't be sure of what order the framelisteners will fire in
#        if (self.stepper.step(time)):
#            self._world.synchronise()

        time = frameEvent.timeSinceLastFrame
        ret = sf.FrameListener.frameStarted(self,frameEvent)

    
        self.delay += time
        if (self.delay > 0.5):
            
            ## Switch shadows
            if (self.Keyboard.isKeyDown(OIS.KC_SPACE)):
                    self.shadowtype += 1
                    if (self.shadowtype > 5):
                        self.shadowtype = 0
                        
                    if self.shadowtype == 0:
                        self.sceneManager.setShadowTechnique (ogre.SHADOWTYPE_NONE) 
                    elif self.shadowtype == 1:
                        self.sceneManager.setShadowTechnique(ogre.SHADOWTYPE_TEXTURE_MODULATIVE)
                        self.sceneManager.setShadowColour(ogre.ColourValue(0.5, 0.5, 0.5))
                        self.sceneManager.setShadowFarDistance(30)
                        if self.root.getRenderSystem().getName().startswith("direct") :
                            self.sceneManager.setShadowTextureSettings(1024, 2)
                        else :
                            self.sceneManager.setShadowTextureSettings(512, 2)
                    elif self.shadowtype == 2:
                        self.sceneManager.setShadowTechnique (ogre.SHADOWTYPE_STENCIL_ADDITIVE) 
                    elif self.shadowtype == 3:
                        self.sceneManager.setShadowTechnique (ogre.SHADOWTYPE_STENCIL_MODULATIVE )  
                    elif self.shadowtype == 4:
                        self.sceneManager.setShadowTechnique (ogre.SHADOWTYPE_TEXTURE_ADDITIVE )     
                        self.sceneManager.setShadowColour((0.5, 0.5, 0.5))
                        self.sceneManager.setShadowFarDistance(30)
                        if self.root.getRenderSystem().getName().startswith("direct"):
                            self.sceneManager.setShadowTextureSettings(1024, 2)
                        else :
                            self.sceneManager.setShadowTextureSettings(512, 2)
                    else:
                        self.sceneManager.setShadowTechnique (ogre.SHADOWTYPE_NONE)
                    self.delay = 0.0
                    
                    
            ## Switch debugging objects on or off
            if (self.Keyboard.isKeyDown(OIS.KC_E)):
                    self.world.setShowDebugGeometries(not self.world.getShowDebugGeometries())
                    self.delay = 0.0
        
                ## Pause or unpause the simulation
            if (self.Keyboard.isKeyDown(OIS.KC_P)):
                    self.paused = not self.paused
                    self.delay = 0.0
        
                    self.stepper.pause(self.paused)
        
                    if self.paused:
                        timeSet = 0.0
                    else:
                        timeSet = 1.0
                    it = self.sceneManager.getMovableObjectIterator(ogre.ParticleSystemFactory.FACTORY_TYPE_NAME)
                    while(it.hasMoreElements()):
                        p = it.getNext()
                        p.setSpeedFactor(timeSet)
                
 
 
        return ret

  



    
#===============================================================================
# # las siguientes 2 funciones se usan  caso de querer saber cuando se pulsa o se suelta una tecla
#===============================================================================
#    def keyPressed(self, frameEvent):
#
#        return True
 
#    def keyReleased(self, frameEvent):
#        # Undo change to the direction vector when the key is released to stop movement.
#
# 


#===============================================================================
# Cambio de vehiculo y conduccion del mismo
#===============================================================================
class VehiculoFrameListener(sf.FrameListener):
    def __init__(self, app,renderWindow,camera,dotOgreOdeLoader):
        sf.FrameListener.__init__(self, renderWindow, camera)
        self.app = app
        self.renderWindow = renderWindow
        self.camera = camera
        self.renderWindow = self.app.renderWindow
        self.TimeUntilNextToggle  = 0
        self.dotOgreOdeLoader = dotOgreOdeLoader
        #Inicializacion de parametros del vehiculo
        self.vehicle = 0
        self.sightNode = 0
        self.cameraNode = camera
        self.sSelectedCar = 2
        self.maxNumCar = 3
        # Reduce move speed
        self.MoveSpeed = 25
        self.TimeUntilNextToggle  = 0
        self.changeCar()
        self.camara = 1
        
        #=======================================================================
        # Crea, y cambia el coche que hay en escena
        #=======================================================================
    def changeCar( self ):
        
        self.sSelectedCar = (self.sSelectedCar + 1) % self.maxNumCar
        
        del self.vehicle

#        Con este metodo cargamos un vehiculo
        self.vehicle = self.dotOgreOdeLoader.loadVehicle (carFileNames[self.sSelectedCar], carNames[self.sSelectedCar])
        # Inicializa el tipo de conduccion
        self.drive = 'R'
        self.vehicle.setPosition((20,0,-20))
        self.sightNode = self.vehicle.getSceneNode().createChildSceneNode("vehiculo_sight",
                                                            (0, 0, 0))
        self.cameraNode = self.vehicle.getSceneNode().createChildSceneNode("vehiculo_camera",
                                                            (0, 0, 0))
        self.updateInfo()
        
        
   #===========================================================================
    # Actualiza la informacion que hay en pantalla    
    #===========================================================================
    def updateInfo( self ):
      
        pOver = ogre.OverlayManager.getSingleton().getByName("OgreOdeDemos/Overlay")
        newInfo = "Info: " + carNames[self.sSelectedCar]
        if self.drive =='R':
            # Switch from rear to front
            newInfo = newInfo + " & Front wheel drive"
        elif self.drive == 'F':
            # Switch from front to all
            newInfo = newInfo + " & All wheel drive"
            # Switch from all to rear
        elif self.drive == '4':
            newInfo = newInfo + " & Rear wheel drive"
        ogre.OverlayManager.getSingleton().getOverlayElement("OgreOdeDemos/Info").setCaption(newInfo)
        print "** Done"
        
    def _setupInput(self):
        # Initialize OIS.
        windowHnd = self.renderWindow.getCustomAttributeInt("WINDOW")
        self.InputManager = OIS.createPythonInputSystem([("WINDOW", str(windowHnd))])
 
        # Create all devices, only catch joystick exceptions since most people use Key/Mouse.
        self.Keyboard = self.InputManager.createInputObjectKeyboard(OIS.OISKeyboard, self.bufferedKeys)
        self.Mouse = self.InputManager.createInputObjectMouse(OIS.OISMouse, self.bufferedMouse)
        try:
            self.Joy = self.InputManager.createInputObjectJoyStick(OIS.OISJoyStick, self.bufferedJoy)
        except:
            self.Joy = False
 
        #Set initial mouse clipping size.
#        self.windowResized(self.renderWindow)
 
        # Register as a Window listener.
        ogre.WindowEventUtilities.addWindowEventListener(self.renderWindow, self);
        
        #=======================================================================
        # SightNode es el nodo al cual apunta la camara, y cameraNode es la propia camara,
        # ambos estan unidos al objeto principal
        #=======================================================================
    def camara3persona(self):
        
                #Cambiar para acercar o alejar la camara, 
        followFactor = 1
        camHeight = 2.0
        camDistance = 7.0
        camLookAhead = 8.0

        q = self.vehicle.getSceneNode().getOrientation()
        toCam = self.vehicle.getSceneNode().getPosition()

        toCam.y += camHeight
        toCam.z -= camDistance * q.zAxis().z
        toCam.x -= camDistance * q.zAxis().x

        self.camera.move( (toCam - self.camera.getPosition()) * followFactor )
        self.camera.lookAt(self.vehicle.getSceneNode().getPosition() + ((self.vehicle.getSceneNode().getOrientation() * ogre.Vector3().UNIT_Z) * camLookAhead))
    
    def camaraLibre(self):
        
    
        self.camera.setPosition((40,20,40))
        self.camera.lookAt((0,0.5,0))
      
        
    def frameStarted(self, frameEvent):
        # Capture and update each device, this will also trigger any listeners.
#        self.Mouse.capture()
        self.Keyboard.capture()

        time = frameEvent.timeSinceLastFrame

        ret = sf.FrameListener.frameStarted(self,frameEvent)
        self.TimeUntilNextToggle -= time
        if (self.TimeUntilNextToggle <= 0) :
           
            
            if self.Keyboard.isKeyDown(OIS.KC_1):
                self.camara = 1
                
            if self.Keyboard.isKeyDown(OIS.KC_2):
                self.camara = 2
                
            if self.Keyboard.isKeyDown(OIS.KC_N):
                self.changeCar()
                self.TimeUntilNextToggle = 0.5
                
                
            # Change the drive mode between front, rear and 4wd
            if self.Keyboard.isKeyDown(OIS.KC_X):
                if self.drive == 'R':
                    self.drive = 'F'

                    self.vehicle.getWheel(0).setPowerFactor(1)
                    self.vehicle.getWheel(1).setPowerFactor(1)
                    self.vehicle.getWheel(2).setPowerFactor(0)
                    self.vehicle.getWheel(3).setPowerFactor(0)

                    self.updateInfo()

                    # Switch from front to all
                elif self.drive ==  'F':
                    self.drive = '4'

                    self.vehicle.getWheel(0).setPowerFactor(0.6)
                    self.vehicle.getWheel(1).setPowerFactor(0.6)
                    self.vehicle.getWheel(2).setPowerFactor(0.4)
                    self.vehicle.getWheel(3).setPowerFactor(0.4)

                    self.updateInfo()

                    # Switch from all to rear
                elif self.drive == '4':
                    self.drive = 'R'

                    self.vehicle.getWheel(0).setPowerFactor(0)
                    self.vehicle.getWheel(1).setPowerFactor(0)
                    self.vehicle.getWheel(2).setPowerFactor(1)
                    self.vehicle.getWheel(3).setPowerFactor(1)

                    self.updateInfo()
                self.TimeUntilNextToggle = 0.5

      
#             print "**** Stepping"
        self.vehicle.setInputs(self.Keyboard.isKeyDown(OIS.KC_LEFT),
                                self.Keyboard.isKeyDown(OIS.KC_RIGHT),
                                self.Keyboard.isKeyDown(OIS.KC_UP),
                                self.Keyboard.isKeyDown(OIS.KC_DOWN))
        self.vehicle.update(time)                
        
        if (self.camara > 1)  :
            self.camaraLibre()
        else :
            self.camara3persona()

        return ret
    

if __name__ == '__main__':
    try:
        application = PrototipoApplication()
        application.go()
    except ogre.OgreException, e:
        print e
        