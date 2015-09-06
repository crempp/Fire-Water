# http://www.panda3d.org/forums/viewtopic.php?t=10581

#from pandac.PandaModules import CardMaker
#from pandac.PandaModules import Texture
#from pandac.PandaModules import TextureStage
#from pandac.PandaModules import Plane
#from pandac.PandaModules import PlaneNode
#from pandac.PandaModules import TransparencyAttrib
#from pandac.PandaModules import CullFaceAttrib
#from pandac.PandaModules import RenderState
#from pandac.PandaModules import ShaderAttrib 

from pandac.PandaModules import CollisionHandlerQueue
from pandac.PandaModules import CollisionNode
from pandac.PandaModules import CollisionRay
from pandac.PandaModules import CollisionTraverser
from pandac.PandaModules import Geom
from pandac.PandaModules import GeomNode
from pandac.PandaModules import GeomTriangles
from pandac.PandaModules import GeomVertexData
from pandac.PandaModules import GeomVertexFormat
from pandac.PandaModules import GeomVertexWriter
from pandac.PandaModules import LineSegs
from pandac.PandaModules import NodePath
from pandac.PandaModules import Vec3
from pandac.PandaModules import Vec4
from pandac.PandaModules import Point3

from pandac.PandaModules import CardMaker, Texture, TextureStage, Plane, \
  PlaneNode, TransparencyAttrib, CullFaceAttrib, RenderState, ShaderAttrib

from panda3d.core import Shader

from GeomObjects import Square

class Water(object):
    def __init__(self, parent):
        self.parent = parent
        self.baseNode = self.parent.attachNewNode(self.__class__.__name__)
        
        x1 = -200
        y1 = -200
        x2 =  200
        y2 =  200
        z  =  0.0
        
        #waterNP = NodePath("Water Node Parent")
        #waterNP.reparentTo(parent)
        
        #sn = self.drawSquare(-100, -100, 0, 100, 100, 0);
        #sn.reparentTo(self.baseNode)
        water = Square(self.baseNode,
                       Point3(x1, y1, 0.2),
                       Point3(x2, y2, 0.2),
                       Vec4(0.0,0.0,0.5,0.5))
        wNp = water.draw()
        t1 = loader.loadTexture( 'assets/textures/wave.png' )
        t1.setWrapU(Texture.WMRepeat)
        t1.setWrapV(Texture.WMRepeat)
        wNp.setTexture(t1)
        
        # Water Shader from
        # http://www.panda3d.org/forums/viewtopic.php?p=70853&sid=53d92b5ae1683bd9458f21d6026ad36e
        # anim: vx, vy, scale, skip
        # distort: offset, strength, refraction factor (0 = perfect mirror,
        #   1 = total refraction), refractivity
        anim = ( .022, -.012, 2.5, 0 )
        distort = ( .1, 2, .5, .45 )
        
        self.buffer = base.win.makeTextureBuffer( 'waterBuffer', 512, 512 )
        self.watercamNP = base.makeCamera( self.buffer )
        
        # Create water surface using a card
        # The surface will be centered and 
        maker = CardMaker( 'water' ) # Water surface
        maker.setFrame( x1, x2, y1, y2 )
        self.waterNP = self.baseNode.attachNewNode( maker.generate() )
        self.waterNP.setPosHpr( ( 0, 0, z ), ( 0, -90, 0 ) )
        self.waterNP.setTransparency( TransparencyAttrib.MAlpha )
        self.waterNP.setTwoSided(True)
        
        # Attach the water shader to the water shader surface
        waterShader = Shader.load("shaders/water.sha")
        self.waterNP.setShader(waterShader)
        self.waterNP.setShaderInput('wateranim',    anim )
        self.waterNP.setShaderInput('waterdistort', distort )
        self.waterNP.setShaderInput('time',         0 )
        
        self.waterPlane = Plane( ( 0, 0, z + 1 ), ( 0, 0, z ) ) # Reflection plane
        PlaneNode( 'waterPlane' ).setPlane( self.waterPlane )
        
        self.buffer.setClearColor( ( 0, 0, 0.5, 1 ) ) # buffer

        self.watercamNP.reparentTo( self.baseNode ) # reflection camera
        cam = self.watercamNP.node()
        cam.getLens().setFov( base.camLens.getFov() )
        cam.getLens().setNearFar( 1, 5000 )
        cam.setInitialState( RenderState.make( CullFaceAttrib.makeReverse() ) )
        cam.setTagStateKey( 'Clipped' )
        cam.setTagState('True', RenderState.make(
          ShaderAttrib.make().setShader(
            loader.loadShader( 'shaders/splut3Clipped.sha' ) ) ) )
        
        tex0 = self.buffer.getTexture() # reflection texture, created in
                                             # realtime by the 'water camera'
        tex0.setWrapU( Texture.WMClamp ); tex0.setWrapV( Texture.WMClamp )
        self.waterNP.setTexture( TextureStage( 'reflection' ), tex0 )
        self.waterNP.setTexture( TextureStage( 'distortion' ),
          loader.loadTexture( 'assets/textures/water.png' ) ) # distortion texture
        
        self.task = taskMgr.add( self.update, 'waterUpdate', sort = 50 )
        
    def remove( self ):
        self.waterNP.removeNode()
        taskMgr.remove( self.task )

    def destroy( self ):
        base.graphicsEngine.removeWindow( WaterNode.buffer )
        base.win.removeDisplayRegion(
          WaterNode.watercamNP.node().getDisplayRegion( 0 ) )
        WaterNode.watercamNP.removeNode()
  
    def update( self, task ):
        self.waterNP.setShaderInput( 'time', task.time ) # time for distortions
        self.watercamNP.setMat( # update the matrix of the reflection camera
          base.camera.getMat() * self.waterPlane.getReflectionMat() )
        return task.cont
        