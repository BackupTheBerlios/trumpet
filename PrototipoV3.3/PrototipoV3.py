import ogre.renderer.OGRE as ogre 
import ogre.io.OIS as OIS 
import ogre.gui.CEGUI as CEGUI
import ogre.physics.OgreOde as OgreOde
import time
from FacultyScene import *
import SampleFramework as sf


STEP_RATE=0.01
ANY_QUERY_MASK                  = 1<<0
ZOMBIE_QUERY_MASK               = 1<<1
GEOMETRY_QUERY_MASK             = 1<<2
VEHICLE_QUERY_MASK              = 1<<3
STATIC_GEOMETRY_QUERY_MASK      = 1<<4

player = False
guia = False

def convertButton(oisID):
        if oisID == OIS.MB_Left:
            return CEGUI.LeftButton
        elif oisID == OIS.MB_Right:
            return CEGUI.RightButton
        elif oisID == OIS.MB_Middle:
            return CEGUI.MiddleButton
        else:
            return CEGUI.LeftButton
        


        


class Application(ogre.FrameListener):

    def __init__ ( self ):
        ogre.FrameListener.__init__(self) 
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
        
        self.CEGUIRenderer = 0
        self.CEGUISystem = 0
        self.menuItems = []

        
    def go(self): 
        self.createRoot() 
        self.defineResources() 
        self.setupRenderSystem() 
        self.createRenderWindow() 
        self.initializeResourceGroups() 
        self.setupScene() 
        self.setupInputSystem() 
        self.setupCEGUI() 
        self.createFrameListener() 
        self.startRenderLoop() 
        self.cleanUp() 
        
    def createRoot(self): 
        self.root = ogre.Root() 
        #pass 
    def defineResources(self): 
        cf = ogre.ConfigFile() 
        cf.load("resources.cfg") 
        seci = cf.getSectionIterator() 
        while seci.hasMoreElements(): 
            secName = seci.peekNextKey() 
            settings = seci.getNext() 
            for item in settings: 
                typeName = item.key 
                archName = item.value 
                ogre.ResourceGroupManager.getSingleton().addResourceLocation(archName, typeName, secName) 
                
    def setupRenderSystem(self): 
        
        if not self.root.restoreConfig() and not self.root.showConfigDialog(): 
            return False
        
    def createRenderWindow(self): 
#        crea el renderWindow a traves de ogre
           self.mWindow = self.root.initialise(True, "Prototipo V3")
            

#            // Crea el render a traves del api win32
#  # Do not add this to the application
#       self.root.initialise(False)
#       hWnd = 0  # Get the hWnd of the application!
#       misc = ogre.NameValuePairList()
#       misc["externalWindowHandle"] = str(int(hWnd))
#       renderWindow = self.root.createRenderWindow("Main RenderWindow", 800, 600, False, misc)
#Note that you still have to call Root.initialise, but the first parameter is set to false. Then, you must get 
      
        #pass 
        
    def initializeResourceGroups(self): 
        ogre.TextureManager.getSingleton().setDefaultNumMipmaps(5) 
        ogre.ResourceGroupManager.getSingleton().initialiseAllResourceGroups() 
        #pass 
        
    def setupScene(self):

        global STEP_RATE, ANY_QUERY_MASK, STATIC_GEOMETRY_QUERY_MASK
        self.sceneManager = self.root.createSceneManager(ogre.ST_GENERIC, "Default SceneManager") 
        ogre.MovableObject.setDefaultQueryFlags (ANY_QUERY_MASK)
        #Crea una camara y anade un viewport
        self.camera = self.sceneManager.createCamera("Camera") 
        ## Position and orient the camera
        self.camera.setPosition(13,4.5,0)
        self.camera.lookAt(0,0.5,0)
        self.camera.setNearClipDistance(0.5)
        self.viewPort = self.root.getAutoCreatedWindow().addViewport(self.camera) 
        ## Set up shadowing
        self.shadowtype=0
        self.sceneManager.setShadowTechnique(ogre.SHADOWTYPE_TEXTURE_MODULATIVE)
        self.sceneManager.setShadowColour((0.5, 0.5, 0.5))
        self.sceneManager.setShadowFarDistance(30)
        if self.root.getRenderSystem().getName().startswith ('direct'): 
            self.sceneManager.setShadowTextureSettings(1024, 2)
        else: 
            self.sceneManager.setShadowTextureSettings(512, 2)
        ## Add some default lighting to the scene
        self.sceneManager.setAmbientLight( (.25, .25, .25) )
        light = self.sceneManager.createLight('MainLight')
        light.setPosition (0, 0, 1)
        light.CastShadows=True
        ## Create a directional light to shadow and light the bodies
        self._spot = self.sceneManager.createLight("Spot")
        self._spot.setType(ogre.Light.LT_DIRECTIONAL)
        self._spot.setDirection(-0.40824828,-0.81649655,-0.40824828)
        self._spot.setCastShadows(True)
        self._spot.setSpecularColour(1,1,0.8)
        ## Give us some sky
        self.sceneManager.setSkyDome(True, 'Examples/CloudySky', 5, 8)
        ## Create the ODE world
        self._world = OgreOde.World(self.sceneManager)
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

        ##  Crear la informacion que aparece en pantalla 
        pOver = ogre.OverlayManager.getSingleton().getByName("OgreOdeDemos/Overlay")    
##        pOver.show()
    
        ## Initialise stuff
        self._test = 0
        self._delay = 1.0
        

        

    def setupInputSystem(self): 
        windowHandle = 0 
        renderWindow = self.root.getAutoCreatedWindow() 
        windowHandle = renderWindow.getCustomAttributeInt("WINDOW") 
        paramList = [("WINDOW", str(windowHandle))] 
        self.inputManager = OIS.createPythonInputSystem(paramList) 
        try: 
            self.keyboard = self.inputManager.createInputObjectKeyboard(OIS.OISKeyboard, False) 
            self.mouse = self.inputManager.createInputObjectMouse(OIS.OISMouse, False) 
            # self.joystick = self.inputManager.createInputObjectJoyStick(OIS.OISJoyStick, False) 
        except Exception, e: 
            raise e 
        #pass 
        
    def setupCEGUI(self): 
     ## setup GUI system
        if CEGUI.Version__.startswith ("0.6"):
           self.renderer = CEGUI.OgreRenderer(self.renderWindow, 
               ogre.RENDER_QUEUE_OVERLAY, False, 3000, self.sceneManager) 
           self.system = CEGUI.System(self.renderer) 
        else:
           self.renderer = CEGUI.OgreRenderer.bootstrapSystem()
           self.system = CEGUI.System.getSingleton()
        ## Select the skin for the CEGUI to use
        if CEGUI.Version__.startswith ("0.6"):
           CEGUI.SchemeManager.getSingleton().loadScheme("TaharezLookSkin.scheme") 
        else:
           CEGUI.SchemeManager.getSingleton().create("TaharezLookSkin.scheme")

        self.system.setDefaultMouseCursor("TaharezLook", "MouseArrow")
        self.system.setDefaultFont("BlueHighway-12")

        windowManager = CEGUI.WindowManager.getSingleton()
        sheet = windowManager.createWindow("DefaultGUISheet", "CEGUIDemo/Sheet")

        jugadorButton = windowManager.createWindow("TaharezLook/Button", "Jugador")
        jugadorButton.setText("Jugador")
        jugadorButton.setSize(CEGUI.UVector2(CEGUI.UDim(0.20, 0), CEGUI.UDim(0.1, 0)))
        jugadorButton.setPosition(CEGUI.UVector2(CEGUI.UDim(0.1,0), CEGUI.UDim(0.5,0)))
        sheet.addChildWindow(jugadorButton)
        
        guiaButton = windowManager.createWindow("TaharezLook/Button", "Guia")
        guiaButton.setText("Guia")
        guiaButton.setSize(CEGUI.UVector2(CEGUI.UDim(0.20, 0), CEGUI.UDim(0.1, 0)))
        guiaButton.setPosition(CEGUI.UVector2(CEGUI.UDim(0.4,0), CEGUI.UDim(0.5,0)))
        sheet.addChildWindow(guiaButton)
        
        opcionesButton = windowManager.createWindow("TaharezLook/Button", "Opciones")
        opcionesButton.setText("Opciones")
        opcionesButton.setSize(CEGUI.UVector2(CEGUI.UDim(0.20, 0), CEGUI.UDim(0.1, 0)))
        opcionesButton.setPosition(CEGUI.UVector2(CEGUI.UDim(0.7,0), CEGUI.UDim(0.5,0)))
        sheet.addChildWindow(opcionesButton)
        
        salirButton = windowManager.createWindow("TaharezLook/Button", "Salir")
        salirButton.setText("Salir")
        salirButton.setSize(CEGUI.UVector2(CEGUI.UDim(0.20, 0), CEGUI.UDim(0.1, 0)))
        salirButton.setPosition(CEGUI.UVector2(CEGUI.UDim(0.4,0), CEGUI.UDim(0.7,0)))
        sheet.addChildWindow(salirButton)
        
        luzButton = windowManager.createWindow("TaharezLook/Button", "Luz")
        luzButton.setText("Luz")
        luzButton.setSize(CEGUI.UVector2(CEGUI.UDim(0.20, 0), CEGUI.UDim(0.1, 0)))
        luzButton.setPosition(CEGUI.UVector2(CEGUI.UDim(0.2,0), CEGUI.UDim(0.5,0)))
        luzButton.setVisible(False)
        sheet.addChildWindow(luzButton)
        
        sombrasButton = windowManager.createWindow("TaharezLook/Button", "Sombras")
        sombrasButton.setText("Sombras")
        sombrasButton.setSize(CEGUI.UVector2(CEGUI.UDim(0.20, 0), CEGUI.UDim(0.1, 0)))
        sombrasButton.setPosition(CEGUI.UVector2(CEGUI.UDim(0.6,0), CEGUI.UDim(0.5,0)))
        sombrasButton.setVisible(False)
        sheet.addChildWindow(sombrasButton)
        
        volverButton = windowManager.createWindow("TaharezLook/Button", "Volver")
        volverButton.setText("Volver")
        volverButton.setSize(CEGUI.UVector2(CEGUI.UDim(0.20, 0), CEGUI.UDim(0.1, 0)))
        volverButton.setPosition(CEGUI.UVector2(CEGUI.UDim(0.4,0), CEGUI.UDim(0.7,0)))
        volverButton.setVisible(False)
        sheet.addChildWindow(volverButton)
        
#===============================================================================
#      CGUI que se muestra 
#===============================================================================
        
        
                    ##
            ## Build a window with some text and formatting options via radio buttons etc
            ##
        textwnd = windowManager.createWindow("TaharezLook/FrameWindow", "ChatWindow")
        sheet.addChildWindow(textwnd)
        textwnd.setPosition(CEGUI.UVector2(cegui_reldim(0.0), cegui_reldim(0.7)))
        textwnd.setMaxSize(CEGUI.UVector2(cegui_reldim(0.75), cegui_reldim(0.75)))
        textwnd.setMinSize(CEGUI.UVector2(cegui_reldim(0.1), cegui_reldim(0.1)))
        textwnd.setSize(CEGUI.UVector2(cegui_reldim(0.4), cegui_reldim(0.3))) 
        textwnd.setCloseButtonEnabled(False)
        textwnd.setText("Chat")
        textwnd.setVisible(False)
        
        st = windowManager.createWindow("TaharezLook/StaticText", "TextWindow/chat")
        textwnd.addChildWindow(st)
        st.setPosition(CEGUI.UVector2(cegui_reldim(0.05), cegui_reldim(0.2))) 
        st.setSize(CEGUI.UVector2(cegui_reldim(0.90), cegui_reldim(0.6)))
                   
           ## Edit box for text entry
        eb = windowManager.createWindow("TaharezLook/Editbox", "TextWindow/text")
        textwnd.addChildWindow(eb)
        eb.setPosition(CEGUI.UVector2(cegui_reldim(0.05), cegui_reldim(0.82))) 
        eb.setMaxSize(CEGUI.UVector2(cegui_reldim(1.0), cegui_reldim(0.04)))
        eb.setSize(CEGUI.UVector2(cegui_reldim(0.90), cegui_reldim(0.2)))



###        Crear un frameWindow y lo anade al root, establece su tamano y posicion
        self.wnd = windowManager.createWindow("TaharezLook/FrameWindow", "MapWindow")
        sheet.addChildWindow(self.wnd)
        self.wnd.setCloseButtonEnabled(False)

        self.wnd.setPosition(CEGUI.UVector2( cegui_reldim(0.7),
                                        cegui_reldim(0)))
        self.wnd.setSize(CEGUI.UVector2( cegui_reldim(0.3),
                                    cegui_reldim(0.3)))
        self.wnd.setText("Faculty Map")
#        # need to do this else we get a crash probably as we are missing an
#        # event handler
#        # disable frame and standard background
        self.wnd.setVisible(False)
        self.wnd.setProperty ("FrameEnabled", "false")
        
        
        


#        ## load image to use as a background
        if CEGUI.Version__.startswith ("0.6"):
            CEGUI.ImagesetManager.getSingleton().createImagesetFromImageFile("BackgroundImage", "PlantaBaja.jpg")
        else:
            CEGUI.ImagesetManager.getSingleton().createFromImageFile("BackgroundImage", "PlantaBaja.jpg")
#    ##  here we will use a StaticImage as the root, then we can use it to place a background image
        background = windowManager.createWindow("TaharezLook/StaticImage" , "background_self.wnd")
#        ## set position and size
        background.setPosition(CEGUI.UVector2(cegui_reldim(0), cegui_reldim( 0)))
        background.setSize(CEGUI.UVector2(cegui_reldim(1), cegui_reldim(1)))
#        ## disable frame and standard background
        background.setProperty("FrameEnabled", "false")
        background.setProperty("BackgroundEnabled", "false")
#        ## set the background image
        background.setProperty("Image", "set:BackgroundImage image:full_image")
        self.wnd.addChildWindow(background)
        self.background = background
        
                 ##
            ## Build a window with some text and formatting options via radio buttons etc
            ##
        textwnd2 = windowManager.createWindow("TaharezLook/FrameWindow","windowWhere")
        background.addChildWindow(textwnd2)
        textwnd2.setPosition(CEGUI.UVector2(cegui_reldim(0.42), cegui_reldim( 0.0))) 
        textwnd2.setMaxSize(CEGUI.UVector2(cegui_reldim(0.75), cegui_reldim( 0.75)))
        textwnd2.setMinSize(CEGUI.UVector2(cegui_reldim(0.1), cegui_reldim( 0.1)))
        textwnd2.setSize(CEGUI.UVector2(cegui_reldim(0.2), cegui_reldim( 0.2)))
        textwnd2.setCloseButtonEnabled(False)
#        textwnd2.setVisible(False)
        textwnd2.setText("Donde quieres ir?")

            
        st2 = windowManager.createWindow("TaharezLook/StaticText", "TextWindow/Where")
        textwnd2.addChildWindow(st2)
        st2.setPosition(CEGUI.UVector2(cegui_reldim(0.05), cegui_reldim( 0.45)))
        st2.setSize(CEGUI.UVector2(cegui_reldim(0.90), cegui_reldim( 0.22)))       
           
        
        
        
        #        ## load image to use as a background
        if CEGUI.Version__.startswith ("0.6"):
            CEGUI.ImagesetManager.getSingleton().createImagesetFromImageFile("Flecha", "flecha.png")
        else:
            CEGUI.ImagesetManager.getSingleton().createFromImageFile("Flecha", "flecha.png")
#    ## here we will use a StaticImage as the root, then we can use it to place a background image
        self.flecha = windowManager.createWindow("TaharezLook/StaticImage" , "Flecha")
#        ## set position and size
        self.flecha.setPosition(CEGUI.UVector2(cegui_reldim(0.5), cegui_reldim(0.5)))
        self.flecha.setSize(CEGUI.UVector2(cegui_reldim(0.03), cegui_reldim(0.03)))
#        ## disable frame and standard background
        self.flecha.setProperty("FrameEnabled", "false")
        self.flecha.setProperty("BackgroundEnabled", "false")
#        ## set the background image
        self.flecha.setProperty("Image", "set:Flecha image:full_image")
        background.addChildWindow(self.flecha)


        
        self.system.setGUISheet(sheet)
 
    def createFrameListener(self): 
        self.exitListener = ExitListener(self.sceneManager,self.keyboard,self._world,self._stepper,self.camera) 
        self.root.addFrameListener(self.exitListener) 
        #pass 
        self.frameListenerCegui = CEGUIFrameListener(self.mWindow, 
                                                     self.camera,
                                                     self.sceneManager, 
                                                     self._test, 
                                                     self._world,
                                                     self)
        self.root.addFrameListener(self.frameListenerCegui)
        
        
        
#        self.frameListenerCegui.showDebugOverlay(True)
        
    def startRenderLoop(self): 
#        self.root.startRendering() 
            while (True):
                   ogre.WindowEventUtilities.messagePump()
                   self.root.renderOneFrame();
                   if(not(self.mWindow.isActive()) and self.mWindow.isVisible()):
                      self.mWindow.update()
#        while(True):
#            self.root.renderOneFrame()
#            self.mWindow.setActive(True)
#        while(True): 
#            self.root.renderOneFrame()
#            self.mWindow.setActive(True)
            
            
    def cleanUp(self): 
        self.inputManager.destroyInputObjectKeyboard(self.keyboard) 
        # self.inputManager.destroyInputObjectMouse(self.mouse) 
        # self.inputManager.destroyInputObjectJoyStick(self.joystick) 
        OIS.InputManager.destroyInputSystem(self.inputManager) 
        self.inputManager = None 
        del self.renderer 
        del self.system 
        del self.exitListener 
        del self.root 
        #pass 
        

class CEGUIFrameListener(sf.FrameListener, OIS.MouseListener, OIS.KeyListener):
 
    def __init__(self, renderWindow, sceneManager, camera, _test, _world, app):
        sf.FrameListener.__init__(self, renderWindow, camera, True, True)
        OIS.MouseListener.__init__(self)
        OIS.KeyListener.__init__(self)
        self.cont = True
        self._test = _test
        self._world = _world
        self.sceneManager = sceneManager
        self.Mouse.setEventCallback(self)
        self.Keyboard.setEventCallback(self)
        self._test = 0
        self._delay = 1.0
        self.map = False
        
        windowManager = CEGUI.WindowManager.getSingleton()

        self.chatShow = windowManager.getWindow("TextWindow/chat")
        self.chatText = windowManager.getWindow("TextWindow/text")
        self.mapWindow = windowManager.getWindow("MapWindow")
        self.windowWhere = windowManager.getWindow("windowWhere")
        
        self.salirButton = CEGUI.WindowManager.getSingleton().getWindow("Salir")
        self.salirButton.subscribeEvent(
                "Clicked", self, "quit")
        
        self.jugadorButton = CEGUI.WindowManager.getSingleton().getWindow("Jugador")
        self.jugadorButton.subscribeEvent(
                "Clicked", self, "cargaFacultad")
        
        self.GuiaButton = CEGUI.WindowManager.getSingleton().getWindow("Guia")
        self.GuiaButton.subscribeEvent(
                "Clicked", self, "cargaGuia")
        
        self.opcionesButton = CEGUI.WindowManager.getSingleton().getWindow("Opciones")
        self.opcionesButton.subscribeEvent(
                "Clicked", self, "cargaOpciones")
        
        self.volverButton = CEGUI.WindowManager.getSingleton().getWindow("Volver")
        self.volverButton.subscribeEvent(
                "Clicked", self, "cargaPrincipal")
        

    def frameStarted(self, evt):
        self.Keyboard.capture()
        self.Mouse.capture()
        
        
        time = evt.timeSinceLastFrame
        self._delay += time
        if (self._delay > 1.0):
            
            if self.Keyboard.isKeyDown(OIS.KC_M):
                if(self.map == False):
        #           Si el mapa esta en peuqeno hay que agrandarlo, y poner los botones 
                    self.map = True
                    self.mapWindow.setPosition(CEGUI.UVector2( cegui_reldim(0),
                                                cegui_reldim(0)))
                    self.mapWindow.setSize(CEGUI.UVector2( cegui_reldim(1),
                                            cegui_reldim(1)))
                    self.windowWhere.setVisible(True)
                        
                        
                else :
                    self.map = False
                    
                    self.mapWindow.setPosition(CEGUI.UVector2( cegui_reldim(0.7),
                                        cegui_reldim(0)))
                    self.mapWindow.setSize(CEGUI.UVector2( cegui_reldim(0.3),
                                    cegui_reldim(0.3)))
                    self.windowWhere.setVisible(False)

        
                self._delay = 0.0
                
                
            if self.Keyboard.isKeyDown(OIS.KC_SPACE):
                ## set text from the edit box...
                self.chatShow.setText(self.chatShow.getText()+"\n"+self.chatText.getText())
                self.chatText.setText("")
                self._delay = 0.0
            
            
        return self.cont and not self.Keyboard.isKeyDown(OIS.KC_ESCAPE)
 
    def quit(self, evt):
        self.cont = False
        return True
    
    def cargaFacultad(self, evt):
        print "F1"
        global player
        self.jugadorButton.setVisible(False)
        self.GuiaButton.setVisible(False)
        self.opcionesButton.setVisible(False)
        self.salirButton.setVisible(False)
#        del self._test
#        self._test = FacultyScene(self._world,self.camera)
        player = True
        return True
   
    def cargaJugador(self, evt):

        return True
    
    def cargaGuia(self, evt):
#        del self._test
#        self._test = FacultyScene(self._world,self.camera,False)
        global guia
        guia = True
        return False
    
    def cargaOpciones(self, evt):
        jugadorButton = CEGUI.WindowManager.getSingleton().getWindow("Jugador")
        jugadorButton.setVisible(False)
        guiaButton = CEGUI.WindowManager.getSingleton().getWindow("Guia")
        guiaButton.setVisible(False)
        opcionesButton = CEGUI.WindowManager.getSingleton().getWindow("Opciones")
        opcionesButton.setVisible(False)
        salirButton = CEGUI.WindowManager.getSingleton().getWindow("Salir")
        salirButton.setVisible(False)
        
        luzButton = CEGUI.WindowManager.getSingleton().getWindow("Luz")
        luzButton.setVisible(True)
        sombrasButton = CEGUI.WindowManager.getSingleton().getWindow("Sombras")
        sombrasButton.setVisible(True)
        volverButton = CEGUI.WindowManager.getSingleton().getWindow("Volver")
        volverButton.setVisible(True)
        return True
    def cargaPrincipal(self, evt):
        jugadorButton = CEGUI.WindowManager.getSingleton().getWindow("Jugador")
        jugadorButton.setVisible(True)
        guiaButton = CEGUI.WindowManager.getSingleton().getWindow("Guia")
        guiaButton.setVisible(True)
        opcionesButton = CEGUI.WindowManager.getSingleton().getWindow("Opciones")
        opcionesButton.setVisible(True)
        salirButton = CEGUI.WindowManager.getSingleton().getWindow("Salir")
        salirButton.setVisible(True)
        
        luzButton = CEGUI.WindowManager.getSingleton().getWindow("Luz")
        luzButton.setVisible(False)
        sombrasButton = CEGUI.WindowManager.getSingleton().getWindow("Sombras")
        sombrasButton.setVisible(False)
        volverButton = CEGUI.WindowManager.getSingleton().getWindow("Volver")
        volverButton.setVisible(False)
        return True
 
    # MouseListener
    def mouseMoved(self, evt):
        CEGUI.System.getSingleton().injectMouseMove(evt.get_state().X.rel, evt.get_state().Y.rel)
 
    def mousePressed(self, evt, id):
       CEGUI.System.getSingleton().injectMouseButtonDown(convertButton(id))
       mousePos = CEGUI.MouseCursor.getSingleton().getPosition()
#       if(mousePos.d_x<300):
#           CEGUI.WindowManager.getSingleton().getWindow("TextWindow/Where").setText("<300")
#       else: 
#           CEGUI.WindowManager.getSingleton().getWindow("TextWindow/Where").setText(">300")

       print mousePos.d_x
       print mousePos.d_y
       
       posX = mousePos.d_x*100/800
       posY = mousePos.d_y*100/600
       
       self.positionOnMap(posX,posY)
     
    def mouseReleased(self, evt, id):
        CEGUI.System.getSingleton().injectMouseButtonUp(convertButton(id))

 
    # KeyListener
    def keyPressed(self, evt):
        ceguiSystem = CEGUI.System.getSingleton()
        ceguiSystem.injectKeyDown(evt.key)
        ceguiSystem.injectChar(evt.text)
        CEGUI.System.getSingleton().injectKeyUp(evt.key)


    def keyReleased(self, evt):
        return True
   
   
    def positionOnMap(self,x,y):
         if((y<42)and (y>25)):
              if((x<60)and(x>47)):
                    CEGUI.WindowManager.getSingleton().getWindow("TextWindow/Where").setText("AULA 2")
              if((x<47)and(x>35)):
                    CEGUI.WindowManager.getSingleton().getWindow("TextWindow/Where").setText("AULA 3")
              if((x<35)and(x>22)):
                    CEGUI.WindowManager.getSingleton().getWindow("TextWindow/Where").setText("AULA 4")
              if((x<22)and(x>10)):
                    CEGUI.WindowManager.getSingleton().getWindow("TextWindow/Where").setText("AULA 5")           
         else :
              CEGUI.WindowManager.getSingleton().getWindow("TextWindow/Where").setText("No registrado")           
                       
    
class ExitListener(ogre.FrameListener): 
    def __init__(self,sceneManager, keyboard,world,stepper,camera): 
        ogre.FrameListener.__init__(self)
        self.sceneManager = sceneManager
        self.keyboard = keyboard
        self._world = world
        self._stepper = stepper
        self.camera = camera
        ## Initialise stuff
        self._test = 0
        self._delay = 1.0
        self._paused = False
        
    def frameStarted(self, evt):
        self.keyboard.capture()
        accion="null"
        ## Set the shadow distance according to how far we are from the plane that receives them
        self.sceneManager.setShadowFarDistance((abs(self.camera.getPosition().y) + 1.0) * 3.0)
    
        ## If we're running a test, tell it that a frame's ended
        if ((self._test) and (not self._paused)):
            if self.keyboard.isKeyDown(OIS.KC_0):
                accion="camara0"
            if self.keyboard.isKeyDown(OIS.KC_1):
                accion="camara1"
            if self.keyboard.isKeyDown(OIS.KC_F2):
                accion="accionF2"
            if self.keyboard.isKeyDown(OIS.KC_F3):
                accion="accionF3"
#                print "F3"
            if self.keyboard.isKeyDown(OIS.KC_F4):
                accion="accionF4"
                
  
            if self.keyboard.isKeyDown(OIS.KC_UP) or self.keyboard.isKeyDown(OIS.KC_W):
                     
                     accion="up"  #
                  
     
            if self.keyboard.isKeyDown(OIS.KC_DOWN) or self.keyboard.isKeyDown(OIS.KC_S):
                    
                     accion= "down"
                  
     
            if self.keyboard.isKeyDown(OIS.KC_LEFT) or self.keyboard.isKeyDown(OIS.KC_A):
         
     
                      accion= "left"
                    
     
            if self.keyboard.isKeyDown(OIS.KC_RIGHT) or self.keyboard.isKeyDown(OIS.KC_D):
                    
                      accion="right"
                   
            
#            print accion
            self._test.frameStarted(evt,evt.timeSinceLastFrame,accion)
            
        return True
    
    def frameEnded(self, evt):
        accion=""
        time = evt.timeSinceLastFrame
        ## If we're running a test, tell it that a frame's ended
        if ((self._test) and (not self._paused)): 
            self._test.frameEnded(evt,time, accion)

        if (self._stepper.step(time)):
            self._world.synchronise()
            
        self._delay += time
        if (self._delay > 1.0):
            changed = False
            if (self.keyboard.isKeyDown(OIS.KC_F1)or(player)):
                global player
                player = False
                print "F1"
                del self._test
                self._test = FacultyScene(self._world,self.camera,True)
                changed = True
                self._delay = 0.0

                if (self.camera.getPosition().z < 10.0):
                    pos = self.camera.getPosition()
                    self.camera.setPosition(pos.x,pos.y,10.0)
                    self.camera.lookAt(0,0,0)
                changed = True
                
            if (self.keyboard.isKeyDown(OIS.KC_F10)or(guia)):
                global guia
                player = False
                print "F1"
                del self._test
                self._test = FacultyScene(self._world,self.camera,False)
                changed = True
                self._delay = 0.0
                
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
            if (self.keyboard.isKeyDown(OIS.KC_SPACE)):
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
            if (self.keyboard.isKeyDown(OIS.KC_E)):
                print "E"
                self._world.setShowDebugGeometries(not self._world.getShowDebugGeometries())
                self._delay = 0.0


            ## Look at the last object, chase it, or not

#            if (self.keyboard.isKeyDown(OIS.KC_M)):
#                print "M"
#                if (self._looking):
#                    if (self._chasing): 
#                        self._looking = self._chasing = False
#                    else:
#                        self._chasing = True
#                else: 
#                    self._looking = True
#                self._delay = 0.0

                
            ## Pause or unpause the simulation
##            if (self.keyboard.isKeyDown(OIS.KC_P)):
##                print "Pause"
##                self._paused = not self._paused
##                self._delay = 0.0
##    
##                self._stepper.pause(self._paused)
##    
##                if self._paused:
##                    timeSet = 0.0
##                else:
##                    timeSet = 1.0
##                it = self.sceneManager.getMovableObjectIterator(ogre.ParticleSystemFactory.FACTORY_TYPE_NAME)
##                while(it.hasMoreElements()):
##                    p = it.getNext()
##                    p.setSpeedFactor(timeSet)
            

if __name__ == '__main__': 
    try: 
        ta = Application() 
        ta.go() 
    except ogre.OgreException, e: 
        print e 
