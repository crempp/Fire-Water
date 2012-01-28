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

from GeomObjects import Square

class Water(object):
    def __init__(self, parent):
        self.parent = parent
        self.baseNode = self.parent.attachNewNode(self.__class__.__name__)
        
        #waterNP = NodePath("Water Node Parent")
        #waterNP.reparentTo(parent)
        
        #sn = self.drawSquare(-100, -100, 0, 100, 100, 0);
        #sn.reparentTo(self.baseNode)
        water = Square(self.baseNode,
                       Point3(-100, -100, 0),
                       Point3(100, 100, 0),
                       Vec4(0.0,0.0,0.5,0.5))
        water.draw()
    
    # drawSquare
    # Draws a square from ll (x1, y2, z1) to ur (x2, y2, z2) returns a node path
    #def drawSquare(self, x1,y1,z1, x2,y2,z2):
    #    format=GeomVertexFormat.getV3n3cpt2()
    #    vdata=GeomVertexData('square', format, Geom.UHStatic)
    #    
    #    vertex=GeomVertexWriter(vdata, 'vertex')
    #    normal=GeomVertexWriter(vdata, 'normal')
    #    color=GeomVertexWriter(vdata, 'color')
    #    texcoord=GeomVertexWriter(vdata, 'texcoord')
    #    
    #    #make sure we draw the sqaure in the right plane
    #    #if x1!=x2:
    #    vertex.addData3f(x1, y1, z1)
    #    vertex.addData3f(x2, y1, z1)
    #    vertex.addData3f(x2, y2, z2)
    #    vertex.addData3f(x1, y2, z2)
    #
    #    normal.addData3f(self.myNormalize(Vec3(2*x1-1, 2*y1-1, 2*z1-1)))
    #    normal.addData3f(self.myNormalize(Vec3(2*x2-1, 2*y1-1, 2*z1-1)))
    #    normal.addData3f(self.myNormalize(Vec3(2*x2-1, 2*y2-1, 2*z2-1)))
    #    normal.addData3f(self.myNormalize(Vec3(2*x1-1, 2*y2-1, 2*z2-1)))
    #    
    #    #adding different colors to the vertex for visibility
    #    color.addData4f(0.0,0.0,0.5,0.5)
    #    color.addData4f(0.0,0.0,0.5,0.5)
    #    color.addData4f(0.0,0.0,0.5,0.5)
    #    color.addData4f(0.0,0.0,0.5,0.5)
    #    
    #    texcoord.addData2f(0.0, 1.0)
    #    texcoord.addData2f(0.0, 0.0)
    #    texcoord.addData2f(1.0, 0.0)
    #    texcoord.addData2f(1.0, 1.0)
    #
    #    #quads arent directly supported by the Geom interface
    #    #you might be interested in the CardMaker class if you are
    #    #interested in rectangle though
    #    tri1=GeomTriangles(Geom.UHStatic)
    #    tri2=GeomTriangles(Geom.UHStatic)
    #    
    #    tri1.addVertex(0)
    #    tri1.addVertex(1)
    #    tri1.addVertex(3)
    #    
    #    tri2.addConsecutiveVertices(1,3)
    #    
    #    tri1.closePrimitive()
    #    tri2.closePrimitive()
    #    
    #    square=Geom(vdata)
    #    square.addPrimitive(tri1)
    #    square.addPrimitive(tri2)
    #    #square.setIntoCollideMask(BitMask32.bit(1))
    #    
    #    squareNP = NodePath(GeomNode('square gnode')) 
    #    squareNP.node().addGeom(square)
    #    squareNP.setTransparency(1) 
    #    squareNP.setAlphaScale(.5) 
    #    squareNP.setTwoSided(True)
    #    #squareNP.setCollideMask(BitMask32.bit(1))
    #    return squareNP
    #
    ## myNormalize
    ## Calculates a normal (How?)
    #def myNormalize(self, myVec):
    #    myVec.normalize()
    #    return myVec
    
#class WaterNode(): 
#  
#    def __init__( self, x1, y1, x2, y2, z, anim, distort ): 
#        # anim: vx, vy, scale, skip 
#        # distort: offset, strength, refraction factor (0 = perfect mirror, 
#        #   1 = total refraction), refractivity 
#    
#        if not hasattr( self, 'buffer' ): 
#          WaterNode.buffer = base.win.makeTextureBuffer( 'waterBuffer', 512, 512 ) 
#        if not hasattr( self, 'watercamNP' ): 
#          WaterNode.watercamNP = base.makeCamera( WaterNode.buffer ) 
#    
#        maker = CardMaker( 'water' ) # Water surface 
#        maker.setFrame( x1, x2, y1, y2 ) 
#    
#        self.waterNP = render.attachNewNode( maker.generate() ) 
#        self.waterNP.setPosHpr( ( 0, 0, z ), ( 0, -90, 0 ) ) 
#        self.waterNP.setTransparency( TransparencyAttrib.MAlpha ) 
#        self.waterNP.setShader( loader.loadShader( 'shaders/water.sha' ) ) 
#        self.waterNP.setShaderInput( 'wateranim', anim ) 
#        self.waterNP.setShaderInput('waterdistort', distort ) 
#        self.waterNP.setShaderInput( 'time', 0 ) 
#        
#        self.waterPlane = Plane( ( 0, 0, z + 1 ), ( 0, 0, z ) ) # Reflection plane 
#        PlaneNode( 'waterPlane' ).setPlane( self.waterPlane ) 
#    
#        WaterNode.buffer.setClearColor( ( 0, 0, 0, 1 ) ) # buffer 
#    
#        WaterNode.watercamNP.reparentTo( render ) # reflection camera 
#        cam = WaterNode.watercamNP.node() 
#        cam.getLens().setFov( base.camLens.getFov() ) 
#        cam.getLens().setNearFar( 1, 5000 ) 
#        cam.setInitialState( RenderState.make( CullFaceAttrib.makeReverse() ) ) 
#        cam.setTagStateKey( 'Clipped' ) 
#        cam.setTagState('True', RenderState.make( 
#          ShaderAttrib.make().setShader( 
#            loader.loadShader( 'shaders/splut3Clipped.sha' ) ) ) ) 
#    
#        tex0 = WaterNode.buffer.getTexture() # reflection texture, created in 
#                                             # realtime by the 'water camera' 
#        tex0.setWrapU( Texture.WMClamp ); tex0.setWrapV( Texture.WMClamp ) 
#        self.waterNP.setTexture( TextureStage( 'reflection' ), tex0 ) 
#        self.waterNP.setTexture( TextureStage( 'distortion' ), 
#          loader.loadTexture( 'assets/textures/water.png' ) ) # distortion texture 
#        
#        self.task = taskMgr.add( self.update, 'waterUpdate', sort = 50 ) 
#      
#    def remove( self ): 
#      self.waterNP.removeNode() 
#      taskMgr.remove( self.task ) 
#  
#    def destroy( self ): 
#      base.graphicsEngine.removeWindow( WaterNode.buffer ) 
#      base.win.removeDisplayRegion( 
#        WaterNode.watercamNP.node().getDisplayRegion( 0 ) ) 
#      WaterNode.watercamNP.removeNode() 
#  
#    def update( self, task ): 
#      self.waterNP.setShaderInput( 'time', task.time ) # time 4 H2O distortions 
#      WaterNode.watercamNP.setMat( # update matrix of the reflection camera 
#        base.camera.getMat() * self.waterPlane.getReflectionMat() ) 
#      return task.cont