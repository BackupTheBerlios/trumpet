# /*
# -----------------------------------------------------------------------------
# This source file is part of OGRE
#     (Object-oriented Graphics Rendering Engine)
# For the latest info, see http:##www.ogre3d.org/

# Copyright (c) 2000-2006 Torus Knot Software Ltd
# Also see acknowledgements in Readme.html

# You may use self sample code for anything you like, it is not covered by the
# LGPL like the rest of the engine.
# -----------------------------------------------------------------------------
# 

###
###  This is a blank template to make it easier to convert existing samples
###
import sys
sys.path.insert(0,'..')
import PythonOgreConfig

import ogre.renderer.OGRE as ogre
import ogre.gui.CEGUI as CEGUI
import ogre.io.OIS as OIS
import SampleFramework

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

class GuiApplication ( SampleFramework.Application ):
   
    def __init__(self):
        SampleFramework.Application.__init__(self)
        self.GUIRenderer=0
        self.GUIsystem =0
        self.EditorGuiSheet=0
        
        
    def __del__(self):
        ##
        ## important that things get deleted int he right order
        ##
        del self.camera
        del self.sceneManager
        del self.frameListener
        try:
            if self.EditorGuiSheet:
                CEGUI.WindowManager.getSingleton().destroyWindow(self.EditorGuiSheet) 
        except:
            pass
        del self.GUIsystem
        del self.GUIRenderer
        del self.root
        del self.renderWindow        
   
 
    ## Just override the mandatory create scene method
    def _createScene(self):
        sceneManager = self.sceneManager
        sceneManager.ambientLight = ogre.ColourValue(0.5, 0.5, 0.5)

        ## Create a skydome
        self.sceneManager.setSkyDome(True, "Examples/CloudySky", 5, 8) 

        ## Create a light
        l = self.sceneManager.createLight("MainLight") 
        l.setPosition(20,80,50) 

#         ## set the default resource groups to be used
#         CEGUI.Imageset.setDefaultResourceGroup("imagesets")
#         CEGUI.Font.setDefaultResourceGroup("fonts")
#         CEGUI.Scheme.setDefaultResourceGroup("schemes")
#         CEGUI.WidgetLookManager.setDefaultResourceGroup("looknfeels")
#         CEGUI.WindowManager.setDefaultResourceGroup("layouts")
#         CEGUI.ScriptModule.setDefaultResourceGroup("lua_scripts")
#         
        ## setup GUI system
        if CEGUI.Version__.startswith ("0.6"):
            self.GUIRenderer = CEGUI.OgreRenderer(self.renderWindow, 
                ogre.RENDER_QUEUE_OVERLAY, False, 3000, self.sceneManager) 
            self.GUIsystem = CEGUI.System(self.GUIRenderer) 
        else:
            self.GUIRenderer = CEGUI.OgreRenderer.bootstrapSystem()
            self.GUIsystem = CEGUI.System.getSingleton()
        
        logger = CEGUI.Logger.getSingleton()
        logger.setLoggingLevel( CEGUI.Informative ) 

        # we will make extensive use of the WindowManager.
        winMgr = CEGUI.WindowManager.getSingleton()

        ## load scheme and set up defaults
        if CEGUI.Version__.startswith ("0.6"):
            CEGUI.SchemeManager.getSingleton().loadScheme("TaharezLookSkin.scheme") 
        else:
            CEGUI.SchemeManager.getSingleton().create("TaharezLookSkin.scheme") 
        self.GUIsystem.setDefaultMouseCursor("TaharezLook",  "MouseArrow") 
        
   
        ## here we will use a StaticImage as the root, then we can use it to place a background image
        background = winMgr.createWindow("TaharezLook/StaticImage", "background_wnd")
        ## set position and size
        background.setPosition(CEGUI.UVector2(cegui_reldim(0), cegui_reldim( 0)))
        background.setSize(CEGUI.UVector2(cegui_reldim(1), cegui_reldim( 1)))
        ## disable frame and standard background
        background.setProperty("FrameEnabled", "false")
        background.setProperty("BackgroundEnabled", "false")

        ## install this as the root GUI sheet
        CEGUI.System.getSingleton().setGUISheet(background)
            
        ## now we create a DefaultWindow which we will attach all the widgets to.  We could
        ## have attached them to the background StaticImage, though we want to be a bit tricky
        ## since we do not wish the background to be faded by the slider - so we create this
        ## container window so we can affect all the other widgets, but leave the background
        ## unchanged.
        sheet = winMgr.createWindow("DefaultWindow", "root_wnd")
        ## attach this to the 'real' root
        background.addChildWindow(sheet)
        

        
        
        ###        Crear un frameWindow y lo anade al root, establece su tamano y posicion
        self.wnd = winMgr.createWindow("TaharezLook/FrameWindow", "Demo Window")
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
        
        
        
            
        ##
        ## Build a window with some text and formatting options via radio buttons etc
        ##
        textwnd = winMgr.createWindow("TaharezLook/FrameWindow", "TextWindow")
        sheet.addChildWindow(textwnd)
        textwnd.setPosition(CEGUI.UVector2(cegui_reldim(0.2), cegui_reldim( 0.2)))
        textwnd.setMaxSize(CEGUI.UVector2(cegui_reldim(0.75), cegui_reldim( 0.75)))
        textwnd.setMinSize(CEGUI.UVector2(cegui_reldim(0.1), cegui_reldim( 0.1)))
        textwnd.setSize(CEGUI.UVector2(cegui_reldim(0.5), cegui_reldim( 0.5)))
        textwnd.setCloseButtonEnabled(False)
        textwnd.setText("Chat")

        st = winMgr.createWindow("TaharezLook/StaticText", "TextWindow/Static")
        textwnd.addChildWindow(st)
        st.setPosition(CEGUI.UVector2(cegui_reldim(0.1), cegui_reldim( 0.2)))
        st.setSize(CEGUI.UVector2(cegui_reldim(0.5), cegui_reldim( 0.6)))
        
        
        ## Edit box for text entry
        eb = winMgr.createWindow("TaharezLook/Editbox", "TextWindow/Editbox1")
        textwnd.addChildWindow(eb)
        eb.setPosition(CEGUI.UVector2(cegui_reldim(0.05), cegui_reldim( 0.85)))
        eb.setMaxSize(CEGUI.UVector2(cegui_reldim(1.0), cegui_reldim( 0.04)))
        eb.setSize(CEGUI.UVector2(cegui_reldim(0.90), cegui_reldim( 0.08)))
        ## subscribe a handler to listen for when the text changes
        eb.subscribeEvent(CEGUI.Window.EventTextChanged, textChangedHandler,"")
        eb.subscribeEvent(CEGUI.Window.EventKeyDown, textKeyDownHandler,"")
#        winMgr.getWindow("TextWindow/Editbox1").setText("Come on then, edit me!")
        
        ## success!
        return True
        
                
        ## now setup any event handlers you want       
        self.setupEventHandlers() 
        
        
    ## Create new frame listener
    def _createFrameListener(self):
        self.frameListener = GuiFrameListener(self.renderWindow, self.camera, self.GUIRenderer) #self.sceneManager)
        self.root.addFrameListener(self.frameListener)
        self.frameListener.showDebugOverlay(False)
        
        
    


    def setupEventHandlers(self):
        wmgr = CEGUI.WindowManager.getSingleton() 
        
#         wmgr.getWindow( "OgreGuiDemo/TabCtrl/Page1/QuitButton").subscribeEvent(
#                             CEGUI.PushButton.EventClicked, self, "handleQuit")
#         wmgr.getWindow("OgreGuiDemo/TabCtrl/Page2/ObjectTypeList").subscribeEvent(
# 				CEGUI.Combobox.EventListSelectionAccepted, self, "handleObjectSelection")

				                
    def handleQuit(self, e):
        self.frameListener.requestShutdown() 
        return True

# /*************************************************************************
#     Free function handler called when editbox text changes
# *************************************************************************/
def textChangedHandler( e):

    ##find the static box
    st = CEGUI.WindowManager.getSingleton().getWindow("TextWindow/Static")

    ## set text from the edit box...
    st.setText(e.window.getText())

    return True
        
def textKeyDownHandler( e):
    """ This doesn't do anything, just makes sure the event subscription is working"""
    ##find the static box
    st = CEGUI.WindowManager.getSingleton().getWindow("TextWindow/Static")
    
    return True        



    
    
if __name__ == '__main__':
    try:
        ta = GuiApplication()
        ta.go()
    except ogre.OgreException, e:
        print e

    
        

