# # /*
# # SimpleScenes_TriMesh.h
# # ---------------------
# # A reimplementation of the ODE triangle mesh collision
# # demo using Ogre and the OgreOde wrapper.
# # */
import ogre.renderer.OGRE as ogre
import ogre.physics.OgreOde as OgreOde

from CreatePlayer import *
import dotscene as DotScene
import os, sys


# # /*
# # The box stacking test extends the box stacking demo, but adds a trimesh!
# # */
class FacultyScene ( CreatePlayer ):
    def __init__ ( self, world ,camera,player):
        
        if(player):
            CreatePlayer.__init__( self, world,camera)
        else:
            CreatePlayer.__init__( self, world,camera)
            
        self.camera = camera
        
        self._facultyNode = self._mgr.getRootSceneNode().createChildSceneNode("DotSceneRoot")
        self._dotscene = DotScene.DotScene("../media_extra/quake/fdi01/Escena01.scene", self._mgr,self._facultyNode)
        
    
        for _mesh in self._dotscene.__getEI__():
            self.create_ODE_Terrain(_mesh,_mesh);
            
            
    def create_ODE_Terrain(self,name,meshFile ):

        entity = self._mgr.createEntity(name,meshFile)
        node = self._mgr.getRootSceneNode().createChildSceneNode(entity.getName())
        node.attachObject(entity)
        node.setPosition(ogre.Vector3(0,3,0))
        node.setOrientation(ogre.Quaternion(ogre.Degree(30),ogre.Vector3().UNIT_Y))
        ei = OgreOde.EntityInformer (entity,node._getFullTransform())
        geom = ei.createStaticTriangleMesh(self._world, self._space)
        entity.setUserAny (geom)
        self._geoms.append(geom)
        
        
        
    ## Destructor, manually destroy the entity and node, since they're 
    ## not associated with a body they won't get deleted automatically
    def _setUpResources ( self ):
        # first load the default resources
        sf.Application._setUpResources ( self )
        
        # Now load any extra resource locations that we might need..  
        # in the example I'm adding the entire tree under the base directory
        bases = ["../media_extra/quake"]
        for base in bases: 
            for directory in os.listdir ( base ):
                fullPath = os.path.join ( base, directory )
                if os.path.isdir( fullPath ):
                    ogre.ResourceGroupManager.getSingleton().addResourceLocation(fullPath,"FileSystem", "General")
               
                    
#    def __del__ ( self ):
#        self._mgr.destroySceneNode("DotSceneRoot")
#        self._mgr.destroyEntity("DotSceneRoot")
       
    ## Return our name for the test application to display
    def getName(self):
        return "Prototipo V2.2"
