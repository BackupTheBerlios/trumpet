# ***************************************************************************
#Prototipo que nos muestra como un vehiculo puede desplazarse por un escenario
#sin poder atravesar las paredes, y moviendo objetos usando PyOgre y PyOdeogre.
#
#Con las teclas de direccion poemos mover el vehiculo
# ***************************************************************************


import sys
sys.path.insert(0,'..')
import PythonOgreConfig
import ogre.renderer.OGRE as ogre
import SampleFramework as sf
import ogre.io.OIS as OIS
import ogre.physics.OgreOde as ode
from SimpleScenes import *

STEP_RATE=0.01
ANY_QUERY_MASK                  = 1<<0
ZOMBIE_QUERY_MASK               = 1<<1
GEOMETRY_QUERY_MASK             = 1<<2
VEHICLE_QUERY_MASK              = 1<<3
STATIC_GEOMETRY_QUERY_MASK      = 1<<4
#------------------------------------------------------------------------------------------------
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

class OdeListener(sf.FrameListener, ode.CollisionListener):
    def __init__(self, renderWindow, camera,time_step,root,world,stepper):
        sf.FrameListener.__init__(self, renderWindow, camera)
        ode.CollisionListener.__init__(self)
        self.world = world
        self.world.setCollisionListener(self)
        self.camera = camera
        self.vehicle = None
        self.world=world
        self.sSelectedCar = 2
        self.maxNumCar = 3
        # Reduce move speed
        self.MoveSpeed = 25
        self.dotOgreOdeLoader = OgreOde.DotLoader(self.world)
        self.TimeUntilNextToggle  = 0
    
        self._stepper_mode_choice = 2
        self._stepper_choice = 3
        
        
        time_scale = 1.0
        max_frame_time =1.0 / 4
        frame_rate = 1.0 / 60
        
        if self._stepper_mode_choice == 0:
            self.stepModeType = OgreOde.StepHandler.BasicStep
        elif self._stepper_mode_choice == 1:
            self.stepModeType = OgreOde.StepHandler.FastStep
        elif self._stepper_mode_choice == 2:
            self.stepModeType = OgreOde.StepHandler.QuickStep
        else:
            self.stepModeType = OgreOde.StepHandler.QuickStep
        
        if self._stepper_choice == 0:
            self._stepper = OgreOde.StepHandler(self.world, OgreOde.StepHandler.QuickStep, time_step,
            max_frame_time,
            time_scale)
        elif self._stepper_choice == 1:
            self._stepper = OgreOde.ExactVariableStepHandler(self.world, OgreOde.StepHandler.QuickStep, time_step,
            max_frame_time,
            time_scale)
        elif self._stepper_choice == 2:
            self._stepper = OgreOde.ForwardFixedStepHandler(self.world, OgreOde.StepHandler.QuickStep, time_step,
            max_frame_time,
            time_scale)
        elif self._stepper_choice == 3:
            self._stepper = OgreOde.ForwardFixedInterpolatedStepHandler(self.world, OgreOde.StepHandler.QuickStep, time_step,
            max_frame_time,
            time_scale)
        

        self._stepper.setAutomatic(OgreOde.StepHandler.AutoMode_PostFrame, root)

        root.getSingleton().setFrameSmoothingPeriod(5.0)

        self.changeCar()

        # Carga la informacion en la pantalla
        pOver = ogre.OverlayManager.getSingleton().getByName("OgreOdeDemos/Overlay")
        ogre.OverlayManager.getSingleton().getOverlayElement("OgreOdeDemos/Name").setCaption("Nombre: "+ "Prototipo")
        ogre.OverlayManager.getSingleton().getOverlayElement("OgreOdeDemos/Keys").setCaption("Teclas: " + "UP/DOWN - Acelerar/Frenar, <-/-> - Girar, X - Cambiar traccion, N - Cambiar coche")
        ogre.OverlayManager.getSingleton().getOverlayElement("OgreOdeDemos/OtherKeys").setCaption("Extra: " + "E - Debug mode")
        pOver.show()
        print "Done"

    #------------------------------------------------------------------------------------------------
    def __del__(self ):
        del self._stepper

    #------------------------------------------------------------------------------------------------
    def changeCar( self ):
        
        self.sSelectedCar = (self.sSelectedCar + 1) % self.maxNumCar
        
        del self.vehicle

#        Con este metodo cargaruamsoun personaje
#        ode._ogreode_.DotLoader.loadRagdoll((object)arg1, (object)filename, (object)object_name)

#        Con este metodo cargamos un vehiculo
        self.vehicle = self.dotOgreOdeLoader.loadVehicle (carFileNames[self.sSelectedCar], carNames[self.sSelectedCar])

        # Inicializa el tipo de conduccion
        self.drive = 'R'

        # Mueve el vehiculo
        v_pos = self.camera.getPosition() + (self.camera.getDirection() * 15.0)
        #v_pos.y += 10
        self.vehicle.setPosition(v_pos)

        self.updateInfo()
       
    #------------------------------------------------------------------------------------------------
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

    #------------------------------------------------------------------------------------------------
    def frameStarted( self, evt):
        time = evt.timeSinceLastFrame

        ret = sf.FrameListener.frameStarted(self,evt)
        self.TimeUntilNextToggle -= time
        if (self.TimeUntilNextToggle <= 0) :
            # Switch debugging objects on or off
            if (self.Keyboard.isKeyDown(OIS.KC_E)):
                World.getSingleton ().setShowDebugObjects(not World.getSingleton ().getShowDebugObjects())
                self.TimeUntilNextToggle = 0.5

            if self.Keyboard.isKeyDown(OIS.KC_N):
                self.changeCar()
                self.TimeUntilNextToggle = 0.5

            if self.Keyboard.isKeyDown(OIS.KC_U):
                self._stepper.pause(False)
                self.TimeUntilNextToggle = 0.5
            if self.Keyboard.isKeyDown(OIS.KC_P):
                self._stepper.pause(True)
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

        if( not self._stepper.isPaused()):
#             print "**** Stepping"
            self.vehicle.setInputs(self.Keyboard.isKeyDown(OIS.KC_LEFT),
                                self.Keyboard.isKeyDown(OIS.KC_RIGHT),
                                self.Keyboard.isKeyDown(OIS.KC_UP),
                                self.Keyboard.isKeyDown(OIS.KC_DOWN))
            self.vehicle.update(time)


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
        return ret

  


    def collision( self, contact) :
        ## Check for collisions between things that are connected and ignore them
        
        g1 = contact.getFirstGeometry()
        g2 = contact.getSecondGeometry()

        
        if (g1 and g2):
            b1 = g1.getBody()
            b2 = g2.getBody()
            if (b1 and b2 and ode.Joint.areConnected(b1, b2)):
               return False 
    
        ## Set the friction at the contact
        ## Infinity didn't get exposed :(
        contact.setCoulombFriction( 9999999999 )    ### OgreOde.Utility.Infinity)
        contact.setBouncyness(0.1)

        ## Yes, this collision is valid
        return True
    
    

class PrototipoApplication (sf.Application):
    def __init__(self):
        
        sf.Application.__init__(self)
        self.world = 0
        self.plane = 0
        self.geoms  = []
        self.bodies = []
        self.joints = []
        self._time_step = 0.01


    def _createScene (self):

        # create World
        self.world = ode.World(self.sceneManager)
        self.world.setGravity((0,-9.80665, 0))
        self.world.setCFM(10e-5)
        self.world.setERP(0.8)
        self.world.setAutoSleep(True)
        self.world.setAutoSleepAverageSamplesCount(10)
        self.world.setContactCorrectionVelocity(1.0)
        space = self.world.getDefaultSpace()
        self.world.setShowDebugGeometries(True)

        sm = self.sceneManager

        sm.ambient = 1,1,1
        time_step = 0.5
        time_scale = 1.7
        max_frame_time = 1.0/4
        self.time_step = time_step
        self.time_scale = 1.0
        self.max_frame_time =1.0 / 4
        self.frame_rate = 1.0 / 60

        self.stepper = ode.StepHandler(self.world,
                                  ode.StepHandler.QuickStep,
                                  time_step,
                                  max_frame_time,
                                  time_scale)


########Con esto creamos un plano en el cual el objeto no se caiga al vacio
        self.plane = ode.InfinitePlaneGeometry(ogre.Plane((0,1,0),0),
                                               self.world,
                                               self.world.getDefaultSpace())



        s = sm.createStaticGeometry('StaticFloor')
        s.setRegionDimensions((160,100,160))
        s.setOrigin((0,-100,0))
        i = 0
        for z in range(-80,80,20):
            for x in range(-80,80,20):
                name = 'Plane_'+str(i)
                i+=1
                ent = sm.createEntity(name,'plane.mesh')
                ent.setQueryFlags(1<<4)
                ent.setUserObject(self.plane)
                s.addEntity(ent,ogre.Vector3(x,0,z))
                #ent.scale = 0.05,0.05,0.05
        s.build()



#===============================================================================
# Objeto en mitad del escenario
#===============================================================================

        ent = sm.createEntity('crate','Barrel.mesh')
        ent.setQueryFlags(1<<2)
        self.node = sm.getRootSceneNode().createChildSceneNode('crate')
        self.node.attachObject(ent)
##        ent.setNormaliseNormals(True)
        ent.setCastShadows(True)

        self.body = ode.Body(self.world)
        self.bodies.append( self.body )

        size = ogre.Vector3(5.31985, 6.11992, 5.31985)

        mass = ode.BoxMass(0.5,size)
        #mass.setDensity(0.01,size)
        geom = ode.BoxGeometry(size,self.world,space)
        self.geoms.append( geom )
        self.body.setMass(mass)

###    Une el nodo y el body
        self.node.attachObject(self.body)
        geom.setBody(self.body)
#        #node.setScale(size)
        ent.setUserObject(geom)

        #w = ogre.Radian(  ode.Utility.randomReal() * 10.0 - 5.0 )
        #x = ode.Utility.randomReal() * 2.0 - 1.0
        #y = ode.Utility.randomReal() * 2.0 - 1.0
        #z = ode.Utility.randomReal() * 2.0 - 1.0
        #body.setOrientation( ogre.Quaternion(w, ogre.Vector3(x,y,z) ) )

        self.body.setPosition((0,80,0))
        #node.showBoundingBox(True)
        
        
        #=======================================================================
        # Piso
        #=======================================================================
        self.create_ODE_Terrain("primerPiso.mesh",(70,0,70),ogre.Vector3(1,1,1));


##     // Create the tri-mesh terrain from a mesh
    def create_ODE_Terrain(self,meshFile,position,size ):
         
         sn = self.sceneManager.getRootSceneNode().createChildSceneNode("TerrainNode",position);
         ent = self.sceneManager.createEntity("Terrain",meshFile);
         sn.attachObject(ent);
         sn.setScale(size);
 
         ei = OgreOde.EntityInformer(ent,sn._getFullTransform());
         self.terrainTriMeshGeom = ei.createStaticTriangleMesh(self.world,self.world.getDefaultSpace());
         
         
        
    def _createCamera(self):
        self.camera = self.sceneManager.createCamera('PlayerCam')
        self.camera.position =0,10,0
        self.camera.lookAt((0,0,0))
        self.camera.nearClipDistance = 1

    def _createViewports (self):
        viewport = self.renderWindow.addViewport(self.camera)
        viewport.backGroundColor = (0,0,0)
        self.camera.aspectRatio = float (viewport.actualWidth) / float (viewport.actualHeight)
       
    def _createFrameListener(self):
        self.frameListener = OdeListener(self.renderWindow,
                                         self.camera,
                                         self._time_step,
                                         self.root,
                                         self.world,
                                         self.stepper)

        self.frameListener.showDebugOverlay(True)
        self.root.addFrameListener(self.frameListener)

    def cleanUp (self):
        ## Stop listening for collisions
        if (self.world.getCollisionListener() == self): 
            self.world.setCollisionListener(None)
        del self.plane ## delete our plane

        ## Run through the list of bodies we're monitoring
        clearList = []

        while len(self.bodies):
            body = self.bodies.pop()
            ## get the scene node this body controls
            node = body.getParentSceneNode()
            if (node):
                name = node.getName()
                clearList+=[ node.getAttachedObject(j)
                      for j in range(node.numAttachedObjects())
                      if node.getAttachedObject(j).getMovableType() != body.getMovableType() ]
                ## Destroy the node by name
                self.sceneManager.getRootSceneNode().removeAndDestroyChild(name)
            ## Delete the body
            del body
    
        ## Remove all the entities we found attached to scene nodes we're controlling
        while len(clearList):
            p = clearList.pop()
            if (p.getMovableType() == "Entity") :
                print "Movables for Deletion %s %s" % (p.getMovableType(),p.getName())
                self.sceneManager.destroyMovableObject(p.getName(), 'Entity')
            elif (p.getMovableType() == "ParticleSystem") :
                self.sceneManager.destroyParticleSystem(p.getName())
            del p

        ## Delete all the collision geometries
        while len(self.geoms):
            p = self.geoms.pop()
            del p

        assert (len(self.geoms)  == 0 )
        assert (len(self.bodies) == 0 )
        assert (len(clearList)   == 0 )

        del self.stepper

if __name__ == '__main__':
    ta = PrototipoApplication ()
    ta.go ()
    ta.cleanUp()
