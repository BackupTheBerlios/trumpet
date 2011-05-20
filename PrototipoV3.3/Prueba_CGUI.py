import SampleFramework as sf
import ogre.renderer.OGRE as ogre
import ogre.io.OIS as OIS
import ogre.gui.CEGUI as CEGUI


import exceptions, random

from CEGUI_framework import *   ## we need the OIS version of the framelistener etc


def convertButton(oisID):
            if oisID == OIS.MB_Left:
                return CEGUI.LeftButton
            elif oisID == OIS.MB_Right:
                return CEGUI.RightButton
            elif oisID == OIS.MB_Middle:
                return CEGUI.MiddleButton
            else:
                return CEGUI.LeftButton

def cegui_reldim ( x ) :
    return CEGUI.UDim((x),0)

CAMERA_NAME = "SceneCamera" 
 
def setupViewport(RenderWindow, SceneManager): 
    RenderWindow.removeAllViewports() 
    cam = SceneManager.getCamera(CAMERA_NAME) 
    vp = RenderWindow.addViewport(cam) 
    vp.setBackgroundColour((0,0,0)) 
    cam.setAspectRatio(float(vp.getActualWidth()) / float(vp.getActualHeight())) 
 
class TutorialListener(sf.FrameListener, OIS.MouseListener, OIS.KeyListener):
 
    def __init__(self, renderWindow, camera,wnd,background,flecha,editBox):
        sf.FrameListener.__init__(self, renderWindow, camera, True, True)
        OIS.MouseListener.__init__(self)
        OIS.KeyListener.__init__(self)
        self.cont = True
        self.wnd = wnd
        self.map = False
        self.backgraound = background
        self.flecha = flecha
        self.editBox = editBox
        self.Mouse.setEventCallback(self)
        self.Keyboard.setEventCallback(self)
        self.contador = 0
        self._delay = 1.0

        windowManager = CEGUI.WindowManager.getSingleton()
        newButton = windowManager.getWindow("CEGUIDemo/NewButton")
        newButton.subscribeEvent(CEGUI.PushButton.EventClicked, self, "New")

 
    def New(self,  e):
        print "NEWWWWWWWWw"
            
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
                    self.wnd.setPosition(CEGUI.UVector2( cegui_reldim(0),
                                                cegui_reldim(0)))
                    self.wnd.setSize(CEGUI.UVector2( cegui_reldim(1),
                                            cegui_reldim(1)))
                        
                        
                else :
                    self.map = False
                    self.wnd.setPosition(CEGUI.UVector2( cegui_reldim(0.7),
                                                    cegui_reldim(0)))
                    self.wnd.setSize(CEGUI.UVector2( cegui_reldim(0.3),
                                                cegui_reldim(0.3)))
                self._delay = 0.0
            
            
            
            if self.Keyboard.isKeyDown(OIS.KC_SPACE):
                self._delay = 0.0
                ##find the static box
                st = CEGUI.WindowManager.getSingleton().getWindow("TextWindow/Static")
            
                ## set text from the edit box...
                st.setText(self.editBox.getText())
                self.editBox.setText("")
                
                
#        self.flecha.setPosition(CEGUI.UVector2(cegui_reldim(self.cont), cegui_reldim(0.5)))
        return self.cont and not self.Keyboard.isKeyDown(OIS.KC_ESCAPE)
 
    def quit(self, evt):
        self.cont = False

 
    # MouseListener
    def mouseMoved(self, evt):
        CEGUI.System.getSingleton().injectMouseMove(evt.get_state().X.rel, evt.get_state().Y.rel)
 
    def mousePressed(self, evt, id):
        CEGUI.System.getSingleton().injectMouseButtonDown(convertButton(id))  
        mousePos = CEGUI.MouseCursor.getSingleton().getPosition()
        print mousePos.d_x
        print mousePos.d_y

 
    def mouseReleased(self, evt, id):
        CEGUI.System.getSingleton().injectMouseButtonUp(convertButton(id))

 
    # KeyListener
    def keyPressed(self, evt):
        ceguiSystem = CEGUI.System.getSingleton()
        ceguiSystem.injectKeyDown(evt.key)
        ceguiSystem.injectChar(evt.text)

 
    def keyReleased(self, evt):
        CEGUI.System.getSingleton().injectKeyUp(evt.key)

      

class TutorialApplication(sf.Application):
 
    def __del__(self):
        if self.system:
            del self.system
        if self.renderer:
            del self.renderer
 
    def _createScene(self):

        ##Inicializa la renderizacin de laCEGUI
##        Parametros:
##                    -el renderWindow
##                    -ogre.RENDER_QUEUE_OVERLAY, que indica que la ceguise
##                    renderiza todo
##                    -True = renderiza despues del render,
##                     False = se renderiza antes
##                    -param max_quads
        ##          obsolete
        ##          -sceneManager
        ## setup GUI system
        if CEGUI.Version__.startswith ("0.6"):
            self.CEGUIRenderer = CEGUI.OgreRenderer(self.renderWindow,
                ogre.RENDER_QUEUE_OVERLAY, False, 3000, self.sceneManager)
            self.CEGUISystem = CEGUI.System(self.CEGUIRenderer)
        else:
            self.CEGUIRenderer = CEGUI.OgreRenderer.bootstrapSystem()
            self.GUIsystem = CEGUI.System.getSingleton()

            ## set the logging level
        CEGUI.Logger.getSingleton().loggingLevel = CEGUI.Insane

                ## Load TaharezLook imageset by making use of the ImagesetManager
        ## singleton.

        if CEGUI.Version__.startswith ("0.6"):
            taharezImages = CEGUI.ImagesetManager.getSingleton().createImageset("TaharezLook.imageset")
        else:
            taharezImages = CEGUI.ImagesetManager.getSingleton().create("TaharezLook.imageset")

##        Establece el cursor del raton
        self.raton = CEGUI.System.getSingleton().setDefaultMouseCursor(taharezImages.getImage("MouseArrow"))



        ## Establecer las fuentes
        if CEGUI.Version__.startswith ("0.6"):
            CEGUI.FontManager.getSingleton().createFont("Commonwealth-10.font")
        else:
            CEGUI.FontManager.getSingleton().create("Commonwealth-10.font")

##        Cargar el "skin"
        CEGUI.WidgetLookManager.getSingleton().parseLookNFeelSpecification("TaharezLook.looknfeel")


        
        ## Use the SchemeManager singleton to load in a scheme that 
        ## registers widgets, for TaharezLook.

        if CEGUI.Version__.startswith ("0.6"):
            CEGUI.SchemeManager.getSingleton().loadScheme("TaharezLookWidgets.scheme")
        else:
            CEGUI.SchemeManager.getSingleton().create("TaharezLookWidgets.scheme")


##        Ahora ya tenemos inicializada la gui, a partir de aqui anadiremos los elementos

        ## Las ventanas y demas elementos los creamos  atraves del windowManager.

        winMgr = CEGUI.WindowManager.getSingleton()
#
###        Creamos una ventana invisible, sobre la que sepondranloselementos
        root = winMgr.createWindow("DefaultWindow", "Root")
#
###        Hacer que las ventanas qeu se pongan en el root sean visibles
        CEGUI.System.getSingleton().setGUISheet(root)
#
###        Crear un frameWindow y lo anade al root, establece su tamano y posicion
        self.wnd = winMgr.createWindow("TaharezLook/FrameWindow", "Demo Window")
        root.addChildWindow(self.wnd)
        self.wnd.setCloseButtonEnabled(False)

        self.wnd.setPosition(CEGUI.UVector2( cegui_reldim(0.7),
                                        cegui_reldim(0)))
        self.wnd.setSize(CEGUI.UVector2( cegui_reldim(0.3),
                                    cegui_reldim(0.3)))
        self.wnd.setText("Faculty Map")
#        # need to do this else we get a crash probably as we are missing an
#        # event handler
#        # disable frame and standard background
        self.wnd.setProperty ("FrameEnabled", "false")


#        ## load image to use as a background
        if CEGUI.Version__.startswith ("0.6"):
            CEGUI.ImagesetManager.getSingleton().createImagesetFromImageFile("BackgroundImage", "PlantaBaja.jpg")
        else:
            CEGUI.ImagesetManager.getSingleton().createFromImageFile("BackgroundImage", "PlantaBaja.jpg")
#    ## here we will use a StaticImage as the root, then we can use it to place a background image
        background = winMgr.createWindow("TaharezLook/StaticImage" , "background_self.wnd")
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
        
        
        
        
        
        #        ## load image to use as a background
        if CEGUI.Version__.startswith ("0.6"):
            CEGUI.ImagesetManager.getSingleton().createImagesetFromImageFile("Flecha", "flecha.png")
        else:
            CEGUI.ImagesetManager.getSingleton().createFromImageFile("Flecha", "flecha.png")
#    ## here we will use a StaticImage as the root, then we can use it to place a background image
        self.flecha = winMgr.createWindow("TaharezLook/StaticImage" , "flecha_self.wnd")
#        ## set position and size
        self.flecha.setPosition(CEGUI.UVector2(cegui_reldim(0.5), cegui_reldim(0.5)))
        self.flecha.setSize(CEGUI.UVector2(cegui_reldim(0.03), cegui_reldim(0.03)))
#        ## disable frame and standard background
        self.flecha.setProperty("FrameEnabled", "false")
        self.flecha.setProperty("BackgroundEnabled", "false")
#        ## set the background image
        self.flecha.setProperty("Image", "set:Flecha image:full_image")
        background.addChildWindow(self.flecha)


##        Pone un boton
        quitButton = winMgr.createWindow("TaharezLook/Button", "CEGUIDemo/NewButton")
        quitButton.setText("New")
        quitButton.setSize(CEGUI.UVector2(CEGUI.UDim(0.15, 0), CEGUI.UDim(0.05, 0)))
        background.addChildWindow(quitButton)


        ##
        ## Build a window with some text and formatting options via radio buttons etc
        ##
        textwnd = winMgr.createWindow("TaharezLook/FrameWindow", "TextWindow")
        root.addChildWindow(textwnd)
        textwnd.setPosition(CEGUI.UVector2(cegui_reldim(0), cegui_reldim( 0)))
        textwnd.setMaxSize(CEGUI.UVector2(cegui_reldim(0.75), cegui_reldim( 0.75)))
        textwnd.setMinSize(CEGUI.UVector2(cegui_reldim(0.1), cegui_reldim( 0.1)))
        textwnd.setSize(CEGUI.UVector2(cegui_reldim(0.8), cegui_reldim( 0.8)))
        textwnd.setCloseButtonEnabled(False)
        textwnd.setText("Chat")
        textwnd.setProperty ("FrameEnabled", "false")

#        textwnd.setProperty ("FrameEnabled", "false")

        st = winMgr.createWindow("TaharezLook/StaticText", "TextWindow/Static")
        textwnd.addChildWindow(st)
        st.setPosition(CEGUI.UVector2(cegui_reldim(0.1), cegui_reldim( 0.2)))
        st.setSize(CEGUI.UVector2(cegui_reldim(0.5), cegui_reldim( 0.6)))
        

        ## Edit box for text entry
        self.eb = winMgr.createWindow("TaharezLook/Editbox", "TextWindow/Editbox1")
        textwnd.addChildWindow(self.eb)
        self.eb.setPosition(CEGUI.UVector2(cegui_reldim(0.05), cegui_reldim( 0.85)))
        self.eb.setMaxSize(CEGUI.UVector2(cegui_reldim(1.0), cegui_reldim( 0.04)))
        self.eb.setSize(CEGUI.UVector2(cegui_reldim(0.90), cegui_reldim( 0.08)))
        ## subscribe a handler to listen for when the text changes
               ## subscribe a handler to listen for when the text changes
#        self.eb.subscribeEvent(CEGUI.Window.EventTextChanged, textChangedHandler,"")
#        self.eb.subscribeEvent(CEGUI.Window.EventKeyDown, textKeyDownHandler,"")

        
        #=======================================================================
        # ETIQUETAS
        #=======================================================================
#        st = winMgr.createWindow("TaharezLook/StaticText", "TextWindow/Group label 2")
#        textwnd.addChildWindow(st)
#        st.setPosition(CEGUI.UVector2(cegui_reldim(0.65), cegui_reldim( 0.53)))
#        st.setSize(CEGUI.UVector2(cegui_reldim(0.35), cegui_reldim( 0.05)))
#        st.setText("Vert. Formatting")
#        ## disable frame and background on static control
#        st.setProperty("FrameEnabled", "False")
#        st.setProperty("BackgroundEnabled", "False")


#        rb.setText("Left Aligned")
#        rb.setText("Right Aligned")
#        rb.setText("Top Aligned")
#        rb.setText("Bottom Aligned")
#        rb.setText("Centred")
      

         


#        ## install this as the root GUI sheet
#        CEGUI.System.getSingleton().setGUISheet(background)
#        ########
#
#            
#        ## now we create a DefaultWindow which we will attach all the widgets to
#        sheet = winMgr.createWindow("DefaultWindow", "root_self.wnd")
#        ## attach this to the 'real' root
#        background.addChildWindow(sheet)
        ########
        
 
        
    def _createFrameListener(self):
        self.frameListener = TutorialListener(self.renderWindow, self.camera,self.wnd,self.background,self.flecha,self.eb)
        self.frameListener.showDebugOverlay(True)
        self.root.addFrameListener(self.frameListener)
        
        

 
if __name__ == '__main__':
    try:
        ta = TutorialApplication()
        ta.go()
    except ogre.OgreException, e:
        print e
