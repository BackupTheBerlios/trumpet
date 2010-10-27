# /*
# SimpleScenesApplication.cpp
# --------------------------
# The main applicatin that handles switching between the
# different scenes in this demo, as well as any common 
# setup and input handling.
# */

## The tests we can display
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


#
### We need a frame listener class
#        
class CollisionFrameListener ( sf.FrameListener,OgreOde.CollisionListener ):
    def __init__( self, demo, renderWindow, camera,world,stepper ):
        sf.FrameListener.__init__(self, renderWindow, camera)
        OgreOde.CollisionListener.__init__(self)
        
        self.world = world
        self.stepper = stepper
        
        self.world.setCollisionListener(self)
       
#    def __del__(self):
#       
#                
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
      

# /*
# Create the scene from an ogre point of view
# and create the common OgreOde things we'll need
# */
class SimpleScenesApplication(sf.Application):
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

    def __del__ ( self ):
        del self._test
        del self._plane
        del self.stepper
        del self._world

        
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
    
        ## Initialise stuff
        self._test = 0
        self._delay = 1.0
        
        
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
    
       

# /*
# The frame listener will let us know when a frame's ended. So we
# can do stuff that we can't do in a frame started event
# e.g. delete things that we can't delete at the start of a frame,
# presumably because some processing has already been done, leaving
# things dangling, like particle systems.
# */
    def frameEnded(self, evt):
        self.Keyboard.capture()
        
        
        time = evt.timeSinceLastFrame
        sceneManager = self.sceneManager
  
        ## Step the world and then synchronise the scene nodes with it, 
        ## we could get this to do this automatically, but we 
        ## can't be sure of what order the framelisteners will fire in
        if (self.stepper.step(time)):
            self._world.synchronise()
    
        self._delay += time
        if (self._delay > 1.0):
            changed = False
    
            
    
    
            ## Switch shadows
            if (Keyboard.isKeyDown(OIS.KC_SPACE)):
                self.shadowtype += 1
                if (self.shadowtype > 5):
                    self.shadowtype = 0
                    
                if self.shadowtype == 0:
                    sceneManager.setShadowTechnique (ogre.SHADOWTYPE_NONE) 
                elif self.shadowtype == 1:
                    sceneManager.setShadowTechnique(ogre.SHADOWTYPE_TEXTURE_MODULATIVE)
                    sceneManager.setShadowColour(ogre.ColourValue(0.5, 0.5, 0.5))
                    sceneManager.setShadowFarDistance(30)
                    if self.root.getRenderSystem().getName().startswith("direct") :
                        sceneManager.setShadowTextureSettings(1024, 2)
                    else :
                        sceneManager.setShadowTextureSettings(512, 2)
                elif self.shadowtype == 2:
                    sceneManager.setShadowTechnique (ogre.SHADOWTYPE_STENCIL_ADDITIVE) 
                elif self.shadowtype == 3:
                    sceneManager.setShadowTechnique (ogre.SHADOWTYPE_STENCIL_MODULATIVE )  
                elif self.shadowtype == 4:
                    sceneManager.setShadowTechnique (ogre.SHADOWTYPE_TEXTURE_ADDITIVE )     
                    sceneManager.setShadowColour((0.5, 0.5, 0.5))
                    sceneManager.setShadowFarDistance(30)
                    if self.root.getRenderSystem().getName().startswith("direct"):
                        sceneManager.setShadowTextureSettings(1024, 2)
                    else :
                        sceneManager.setShadowTextureSettings(512, 2)
                else:
                    sceneManager.setShadowTechnique (ogre.SHADOWTYPE_NONE) 
                self._delay = 0.0
    
           
    
            ## Switch debugging objects on or off
            if (self.Keyboard.isKeyDown(OIS.KC_E)):
                print "E"
                self.world.setShowDebugGeometries(not self._world.getShowDebugGeometries())
                self._delay = 0.0
    
            ## Pause or unpause the simulation
            if (Keyboard.isKeyDown(OIS.KC_P)):
                self._paused = not self._paused
                self._delay = 0.0
    
                self._stepper.pause(self._paused)
    
                if self._paused:
                    timeSet = 0.0
                else:
                    timeSet = 1.0
                it = sceneManager.getMovableObjectIterator(ogre.ParticleSystemFactory.FACTORY_TYPE_NAME)
                while(it.hasMoreElements()):
                    p = it.getNext()
                    p.setSpeedFactor(timeSet)
                
#    ## we need to register the framelistener
    def _createFrameListener(self):
        ## note we pass ourselves as the demo to the framelistener
        self.frameListener = CollisionFrameListener(self, self.renderWindow, self.camera,self.world,self.stepper)
        self.root.addFrameListener(self.frameListener)
       


if __name__ == '__main__':
    try:
        application = SimpleScenesApplication()
        application.go()
    except ogre.OgreException, e:
        print e
        