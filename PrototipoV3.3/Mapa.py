'''
Created on 14/05/2011

@author: Fer
'''
import SampleFramework as sf
import ogre.renderer.OGRE as ogre
import ogre.io.OIS as OIS
import ogre.gui.CEGUI as CEGUI
 
 
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
       
class TutorialListener(sf.FrameListener, OIS.MouseListener, OIS.KeyListener):
 
    def __init__(self, renderWindow, camera):
        sf.FrameListener.__init__(self, renderWindow, camera, True, True)
        OIS.MouseListener.__init__(self)
        OIS.KeyListener.__init__(self)
        self.cont = True
        self.Mouse.setEventCallback(self)
        self.Keyboard.setEventCallback(self)
        self._delay = 1.0
        self.map = False

        
        windowManager = CEGUI.WindowManager.getSingleton()

        self.chatShow = windowManager.getWindow("TextWindow/chat")
        self.chatText = windowManager.getWindow("TextWindow/text")
        self.mapWindow = windowManager.getWindow("MapWindow")
        self.windowWhere = windowManager.getWindow("windowWhere")

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
 
    # MouseListener
    def mouseMoved(self, evt):
       CEGUI.System.getSingleton().injectMouseMove(evt.get_state().X.rel, evt.get_state().Y.rel)
 
    def mousePressed(self, evt, id):
       CEGUI.System.getSingleton().injectMouseButtonDown(convertButton(id))
       mousePos = CEGUI.MouseCursor.getSingleton().getPosition()
       if(mousePos.d_x<300):
           CEGUI.WindowManager.getSingleton().getWindow("TextWindow/Where").setText("<300")
       else: 
           CEGUI.WindowManager.getSingleton().getWindow("TextWindow/Where").setText(">300")

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
 
class Mapa(sf.Application):
 
    def __del__(self):
        if self.system:
            del self.system
        if self.renderer:
            del self.renderer
 
    def __init__(self):
        pass
    def _createScene(self):
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
           
           winMgr = CEGUI.WindowManager.getSingleton()
           sheet = winMgr.createWindow("DefaultGUISheet", "CEGUIDemo/Sheet")

            ##
            ## Build a window with some text and formatting options via radio buttons etc
            ##
           textwnd = winMgr.createWindow("TaharezLook/FrameWindow", "ChatWindow")
           sheet.addChildWindow(textwnd)
           textwnd.setPosition(CEGUI.UVector2(cegui_reldim(0.0), cegui_reldim( 0.7)))
           textwnd.setMaxSize(CEGUI.UVector2(cegui_reldim(0.75), cegui_reldim( 0.75)))
           textwnd.setMinSize(CEGUI.UVector2(cegui_reldim(0.1), cegui_reldim( 0.1)))
           textwnd.setSize(CEGUI.UVector2(cegui_reldim(0.4), cegui_reldim( 0.3)))
           textwnd.setCloseButtonEnabled(False)
           textwnd.setText("Chat")
        
           st = winMgr.createWindow("TaharezLook/StaticText", "TextWindow/chat")
           textwnd.addChildWindow(st)
           st.setPosition(CEGUI.UVector2(cegui_reldim(0.05), cegui_reldim( 0.2)))
           st.setSize(CEGUI.UVector2(cegui_reldim(0.90), cegui_reldim( 0.6)))
                   
           ## Edit box for text entry
           eb = winMgr.createWindow("TaharezLook/Editbox", "TextWindow/text")
           textwnd.addChildWindow(eb)
           eb.setPosition(CEGUI.UVector2(cegui_reldim(0.05), cegui_reldim( 0.82)))
           eb.setMaxSize(CEGUI.UVector2(cegui_reldim(1.0), cegui_reldim( 0.04)))
           eb.setSize(CEGUI.UVector2(cegui_reldim(0.90), cegui_reldim( 0.2)))
           ## subscribe a handler to listen for when the text changes
#        eb.subscribeEvent(CEGUI.Window.EventTextChanged, textChangedHandler,"")
#        eb.subscribeEvent(CEGUI.Window.EventKeyDown, textKeyDownHandler,"")
#        winMgr.getWindow("TextWindow/Editbox1").setText("Come on then, edit me!")


###        Crear un frameWindow y lo anade al root, establece su tamano y posicion
           self.wnd = winMgr.createWindow("TaharezLook/FrameWindow", "MapWindow")
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
           self.wnd.setProperty ("FrameEnabled", "false")
        
        
        


#        ## load image to use as a background
           if CEGUI.Version__.startswith ("0.6"):
            CEGUI.ImagesetManager.getSingleton().createImagesetFromImageFile("BackgroundImage", "PlantaBaja.jpg")
           else:
            CEGUI.ImagesetManager.getSingleton().createFromImageFile("BackgroundImage", "PlantaBaja.jpg")
#    ##  here we will use a StaticImage as the root, then we can use it to place a background image
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
        
                 ##
            ## Build a window with some text and formatting options via radio buttons etc
            ##
           textwnd2 = winMgr.createWindow("TaharezLook/FrameWindow","windowWhere")
           background.addChildWindow(textwnd2)
           textwnd2.setPosition(CEGUI.UVector2(cegui_reldim(0.42), cegui_reldim( 0.0)))
           textwnd2.setMaxSize(CEGUI.UVector2(cegui_reldim(0.75), cegui_reldim( 0.75)))
           textwnd2.setMinSize(CEGUI.UVector2(cegui_reldim(0.1), cegui_reldim( 0.1)))
           textwnd2.setSize(CEGUI.UVector2(cegui_reldim(0.2), cegui_reldim( 0.2)))
           textwnd2.setCloseButtonEnabled(False)
           textwnd2.setVisible(False)
           textwnd2.setText("Donde quieres ir?")

            
           st2 = winMgr.createWindow("TaharezLook/StaticText", "TextWindow/Where")
           textwnd2.addChildWindow(st2)
           st2.setPosition(CEGUI.UVector2(cegui_reldim(0.05), cegui_reldim( 0.45)))
           st2.setSize(CEGUI.UVector2(cegui_reldim(0.90), cegui_reldim( 0.22)))       
           
        
        
        
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
        
        
     
    
           self.system.setGUISheet(sheet)
           
           
    def _createFrameListener(self):
        self.frameListener = TutorialListener(self.renderWindow, self.camera)
        self.frameListener.showDebugOverlay(True)
        self.root.addFrameListener(self.frameListener)
 
if __name__ == '__main__':
    try:
        ta = Mapa()
        ta.go()
    except ogre.OgreException, e:
        print e