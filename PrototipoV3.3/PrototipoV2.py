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



from FacultyScene import *



STEP_RATE=0.01
ANY_QUERY_MASK                  = 1<<0
ZOMBIE_QUERY_MASK               = 1<<1
GEOMETRY_QUERY_MASK             = 1<<2
VEHICLE_QUERY_MASK              = 1<<3
STATIC_GEOMETRY_QUERY_MASK      = 1<<4
## We need a frame listener class
        
class PrototipoV2FrameListener ( sf.FrameListener ):
    def __init__( self, prototipo, renderWindow, camera ):
        sf.FrameListener.__init__(self, renderWindow, camera)
        self._prototipo = prototipo
    def __del__(self):
        sf.FrameListener.__del__(self)
                
    def frameStarted(self, evt):
        ## Do the default demo input handling and keep our UI display
        ## in sync with the other stuff (frame rate, logo, etc)
        show = self.statisticsOn
        bOK = sf.FrameListener.frameStarted(self, evt)
        if (self.statisticsOn != show):
            pOver = ogre.OverlayManager.getSingleton().getByName("OgreOdeDemos/Overlay")    
            if (pOver):
                if (self.statisticsOn) :
                    pOver.show()
                else :
                    pOver.hide()
                    
        ## Tell the demo application that it needs to handle input
        if bOK:

            self._prototipo.frameStarted(evt, self.Keyboard, self.Mouse)  #we pass the keyboard etc to the main app framelistener

        else:
            ## NOTE:  Because we are holding a pointer to the main app (or demo app) we need to 
            ## delete it here first otherwise we get a crash..

            del self._prototipo  
        ## Quit or carry on according to the normal demo input
        return bOK
    
    # 
    # The frame listener is informed after every frame
    # 
    def frameEnded(self, evt):
        ## Tell our demo that the frame's ended before doing default processing

        self._prototipo.frameEnded(evt, self.Keyboard, self.Mouse)

        return sf.FrameListener.frameEnded(self, evt)


# /*
# Create the scene from an ogre point of view
# and create the common OgreOde things we'll need
# */
class PrototipoV2(sf.Application):
    def __init__ ( self ):
        sf.Application.__init__(self)
        self._prototipo = 0
   #     self._plane = 0     En el futuro a lo mejor es recomendable situar todo sobre un plano infinito
        self._stepper = 0   
        self._world = 0
        self._delay=0.0
        self._spot=None
        self._time_elapsed = 0.0
        self._time_step = 0.1 ## SimpleScenes::STEP_RATE
        self._looking = self._chasing = False
        self._paused = False
        self.render = None;
    
        #self.accion = ""
    def __del__ ( self ):
        
      
        del self._stepper
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
        self._spot = sceneManager.createLight("Spot")
        self._spot.setType(ogre.Light.LT_DIRECTIONAL)
        self._spot.setDirection(-0.40824828,-0.81649655,-0.40824828)
        self._spot.setCastShadows(True)
        self._spot.setSpecularColour(1,1,0.8)

        ## Give us some sky
        sceneManager.setSkyDome(True, 'Examples/CloudySky', 5, 8)
    
        ## Position and orient the camera
        self.camera.setPosition(13,4.5,0)
        self.camera.lookAt(0,0.5,0)
        self.camera.setNearClipDistance(0.5)

        ## Create the ODE world
        self._world = OgreOde.World(sceneManager)
    
        self._world.setGravity( (0,-18700,0) )
        
        _stepper_mode_choice = 2
        _stepper_choice = 3
        time_scale = 1.7
        max_frame_time = 1.0 / 4.0
        frame_rate = 1.0 / 60.0


        if _stepper_mode_choice ==0:    stepModeType = OgreOde.StepHandler.BasicStep
        elif _stepper_mode_choice ==1:  stepModeType = OgreOde.StepHandler.FastStep
        elif _stepper_mode_choice ==2:  stepModeType = OgreOde.StepHandler.QuickStep
        else: stepModeType = OgreOde.StepHandler.QuickStep

        if _stepper_choice == 0:
            self._stepper = OgreOde.StepHandler(self._world, StepHandler.QuickStep, 
                STEP_RATE, max_frame_time,  time_scale)
        elif _stepper_choice == 1:
           self._stepper =  OgreOde.ExactVariableStepHandler(self._world, 
                stepModeType, 
                STEP_RATE,
                max_frame_time,
                time_scale)
        
        elif _stepper_choice == 2:
            self._stepper = OgreOde.ForwardFixedStepHandler(self._world, 
                stepModeType, 
                STEP_RATE,
                max_frame_time,
                time_scale)
        else:
            self._stepper = OgreOde.ForwardFixedInterpolatedStepHandler (self._world, 
                stepModeType, 
                STEP_RATE,
                frame_rate,
                max_frame_time,
                time_scale)
            
#            

        pOver = ogre.OverlayManager.getSingleton().getByName("OgreOdeDemos/Overlay")    
        pOver.show()
    
        ## Initialise stuff
        self._test = 0
        self._delay = 1.0

# 
# The frame listener will notify us when a frame's 
# about to be started, so we can update stuff

  
# 
    def frameStarted (self, evt, Keyboard, Mouse):

        
        accion=""
        ## Set the shadow distance according to how far we are from the plane that receives them
        self.sceneManager.setShadowFarDistance((abs(self.camera.getPosition().y) + 1.0) * 3.0)
    
        ## If we're running a test, tell it that a frame's ended
        if ((self._test) and (not self._paused)):
            if Keyboard.isKeyDown(OIS.KC_0):
                accion="camara0"
            if Keyboard.isKeyDown(OIS.KC_1):
                accion="camara1"
            if Keyboard.isKeyDown(OIS.KC_F2):
                accion="accionF2"
            if Keyboard.isKeyDown(OIS.KC_F3):
                accion="accionF3"
#                print "F3"
            if Keyboard.isKeyDown(OIS.KC_F4):
                accion="accionF4"
            if Keyboard.isKeyDown(OIS.KC_UP) or Keyboard.isKeyDown(OIS.KC_W):
                
                accion="up"  #
                 

            if Keyboard.isKeyDown(OIS.KC_DOWN) or Keyboard.isKeyDown(OIS.KC_S):
               
                accion= "down"

            if Keyboard.isKeyDown(OIS.KC_LEFT) or Keyboard.isKeyDown(OIS.KC_A):
    

                 accion= "left"

            if Keyboard.isKeyDown(OIS.KC_RIGHT) or Keyboard.isKeyDown(OIS.KC_D):
               
                 accion="right"
            
#            print accion
            self._test.frameStarted(evt,evt.timeSinceLastFrame,accion)



    def frameEnded(self, evt, Keyboard, Mouse):
        
        accion=""
        time = evt.timeSinceLastFrame
        sceneManager = self.sceneManager
        ## If we're running a test, tell it that a frame's ended
        if ((self._test) and (not self._paused)): 
            self._test.frameEnded(evt,time, accion)

        if (self._stepper.step(time)):
            self._world.synchronise()
    
        self._delay += time
        if (self._delay > 1.0):
            changed = False

            if (Keyboard.isKeyDown(OIS.KC_F1)):
                del self._test
                self._test = FacultyScene(self._world,self.camera)
                changed = True
 
    
                if (self.camera.getPosition().z < 10.0):
                    pos = self.camera.getPosition()
                    self.camera.setPosition(pos.x,pos.y,10.0)
                    self.camera.lookAt(0,0,0)
                changed = True

            if ((self._test) and (changed)):
                ## Register it with the stepper, so we can (for example) add forces before each step
                self._stepper.setStepListener(self._test)
    
                ## Set the UI to show the test's details
                ogre.OverlayManager.getSingleton().getOverlayElement("OgreOdeDemos/Name")\
                                .setCaption(ogre.UTFString("Name: " + self._test.getName()))
                ogre.OverlayManager.getSingleton().getOverlayElement("OgreOdeDemos/Keys")\
                                .setCaption(ogre.UTFString("Keys: "))
    
                self._delay = 0.0
    
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
    
            ## Look at the last object, chase it, or not

            if (Keyboard.isKeyDown(OIS.KC_M)):
                if (self._looking):
                    if (self._chasing): 
                        self._looking = self._chasing = False
                    else:
                        self._chasing = True
                else: 
                    self._looking = True
                self._delay = 0.0
    
            ## Switch debugging objects on or off
            if (Keyboard.isKeyDown(OIS.KC_E)):
                self._world.setShowDebugGeometries(not self._world.getShowDebugGeometries())
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
                
    ## we need to register the framelistener
    def _createFrameListener(self):
        ## note we pass ourselves as the demo to the framelistener
        self.frameListener = PrototipoV2FrameListener(self, self.renderWindow, self.camera)
        self.root.addFrameListener(self.frameListener)
        
        

       


if __name__ == '__main__':
    try:
        application = PrototipoV2()
        application.go()
#        while 1:
##
##        
##            # todo lo que os de la gana
##            
#            application.renderOneFrame()
##        application.go()
    except ogre.OgreException, e:
        print e
        
