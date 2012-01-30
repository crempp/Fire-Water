''' GeomObjects.py
    
    A collection of geometry objects.

    Author:         Chad Rempp
    Date:           2009/05/07
    License:        GNU LGPL v3
    Todo:           
'''
# Python imports
from __future__ import division
import math

# Panda imports
from pandac.PandaModules import AntialiasAttrib
from pandac.PandaModules import BillboardEffect
from pandac.PandaModules import DepthTestAttrib
from pandac.PandaModules import Geom
from pandac.PandaModules import GeomLines
from pandac.PandaModules import GeomTriangles
from pandac.PandaModules import GeomVertexData
from pandac.PandaModules import GeomVertexFormat
from pandac.PandaModules import GeomVertexWriter
from pandac.PandaModules import LineSegs
from pandac.PandaModules import NodePath
from pandac.PandaModules import RenderAttrib
from pandac.PandaModules import TransparencyAttrib
from pandac.PandaModules import Vec3
from pandac.PandaModules import Vec4
from pandac.PandaModules import GeomNode
from pandac.PandaModules import Plane
from pandac.PandaModules import Point3

# Game imports
import Event

class CircleBB(object):
    _EDGES = 40
    _np = NodePath()
    def __init__(self, parent, pos=Vec3(0, 0, 0), size=1, color=Vec4(0, 0, 0, 1)):
        print("  Creating circle at " + str(pos))
        self.aaLevel= 16
        self.pos = pos
        self.size = size
        self.color = color
        self._np = self.draw()
        self._np.setTwoSided(True)
        self._np.setTransparency(1)
        self._np.setAttrib(DepthTestAttrib.make(RenderAttrib.MNone))
        self._np.setEffect(BillboardEffect.makePointEye())
        if self.aaLevel > 0:
            self._np.setAntialias(AntialiasAttrib.MPolygon, self.aaLevel)
        self._np.reparentTo(parent)
        
    def draw(self):
        format=GeomVertexFormat.getV3n3cpt2()
        vdata=GeomVertexData('square', format, Geom.UHDynamic)
        vertex=GeomVertexWriter(vdata, 'vertex')
        normal=GeomVertexWriter(vdata, 'normal')
        color=GeomVertexWriter(vdata, 'color')
        circle=Geom(vdata)
        # Create vertices
        vertex.addData3f(self.pos)
        color.addData4f(self.color)
        for v in range(self._EDGES):
            x = self.pos.getX() + (self.size * math.cos((2*math.pi/self._EDGES)*v))
            y = self.pos.getY() + (self.size * math.sin((2*math.pi/self._EDGES)*v))
            z = self.pos.getZ()
            vertex.addData3f(x, y, z)
            color.addData4f(self.color)
        
        # Create triangles
        for t in range(self._EDGES):
            tri = GeomTriangles(Geom.UHDynamic)
            tri.addVertex(0)
            tri.addVertex(t+1)
            if (t+2) > self._EDGES:
                tri.addVertex(1)
            else:
                tri.addVertex(t+2)
            tri.closePrimitive()
            circle.addPrimitive(tri)
        
        gn = GeomNode('Circle')
        gn.addGeom(circle)
        np = NodePath(gn)
        np.setHpr(0, 90, 0)
        return np
        
    def removeNode(self):
        self._np.removeNode()
        
    def __del__(self):
        self.removeNode()

class SelectionIndicator(object):
    _np = NodePath()
    _currHpr = Vec3(0, 0, 0)
    _color=Vec4(0.3, 0.3, 0.8, 1)
    
    def __init__(self, parent, size=1):
        LOG.debug("[SelectionIndicator] Initializing")
        self.aaLevel = 16
        self.size = size
        self._np = loader.loadModelCopy("data/models/ribbon.egg")
        self._np.setScale(10)
        self._np.setHpr(self._currHpr)
        self._np.setTwoSided(True)
        if self.aaLevel > 0:
            self._np.setAntialias(AntialiasAttrib.MLine, self.aaLevel)
        self._np.reparentTo(parent)
        taskMgr.add(self.rotate, 'Selection Rotation Task')
        
    def rotate(self, Task):
        self._currHpr.setX(self._currHpr.getX() + 0.01)
        self._np.setHpr(self._currHpr)
        return Task.cont
        
    def removeNode(self):
        taskMgr.remove('Selection Rotation Task')
        self._np.removeNode()
        
    def __del__(self):
        self.removeNode()
    
    
class MoveCursor(object):
    _EDGES      = 40
    _zPos       = 0
    _movingUp   = False
    _movingDown = False
    _color      = Vec4(0.3, 0.3, 0.8, 1)
    _currentPos = Vec3(0, 0, 0)
    
    def __init__(self, parent, entity, foot=1):
        # We keep a reference to the entity
        self.entity = entity
        
        # Setup the components of the cursor
        self._moveRadCircleNP  = NodePath("Movement Radius Node")
        self._moveLine         = LineSegs()
        self._moveLineNP       = NodePath("Movement Direction Line Node")
        self._moveZLine        = LineSegs()
        self._moveZLineNP      = NodePath("Movement Z Line Node")
        self._moveZFootNP      = NodePath("Movement Z Foot Node")
        self._moveFootCircle   = LineSegs()
        self._moveFootCircleNP = NodePath("Movement Foot Circle Node")
        self._np = NodePath("Movement Node")
        
        self.aaLevel = 16
        self.parent = parent
        self.start  = Vec3(0, 0, 0)
        self.moveRad = entity.moveRadius
        self.footRad = foot
        self.plane = Plane(Vec3(0, 0, 1), Point3(0, 0, 0))
        
        if self.aaLevel > 0:
            self._np.setAntialias(AntialiasAttrib.MLine, self.aaLevel)
        
        x = 0
        y = 0
        z = 0
        # Draw movement radius
        moveRadLine = LineSegs()
        moveRadLine.setThickness(1)
        moveRadLine.setColor(self._color)
        moveRadLine.moveTo(self.moveRad, 0, 0)
        for i in range(self._EDGES + 1):
            newX = (self.moveRad * math.cos((2*math.pi/self._EDGES)*i))
            newY = (self.moveRad * math.sin((2*math.pi/self._EDGES)*i))
            moveRadLine.drawTo(newX, newY, 0)
        moveRadGeom = moveRadLine.create()
        self._moveRadCircleNP = NodePath(moveRadGeom)
        self._moveRadCircleNP.reparentTo(self._np)
        
        # Draw movement foot circle
        self._moveFootCircle.setThickness(1)
        self._moveFootCircle.setColor(self._color)
        self._moveFootCircle.moveTo(self.footRad, 0, 0)
        for i in range(self._EDGES):
            newX = (self.footRad * math.cos((2*math.pi/self._EDGES)*i))
            newY = (self.footRad * math.sin((2*math.pi/self._EDGES)*i))
            self._moveFootCircle.drawTo(newX, newY, 0)
        self._moveFootCircle.drawTo(self.footRad, 0, 0)
        moveFootCircleGeom = self._moveFootCircle.create()
        self._moveFootCircleNP = NodePath(moveFootCircleGeom)
        self._moveFootCircleNP.reparentTo(self._np)
        
        # Draw movement direction line
        self._moveLine.setThickness(1)
        self._moveLine.setColor(self._color)
        self._moveLine.moveTo(0, 0, 0)
        self._moveLine.drawTo(x, y, z) 
        self.moveLineGO = self._moveLine.create(True)
        self._moveLineNP = NodePath(self.moveLineGO)
        self._moveLineNP.reparentTo(self._np)
        
    def updateMovePos(self, Task):
        # endPos must be transformed in the the coord sys of the model
        m_pos = self.getMouseXY()
        if m_pos is not None:
            # Transform current mouse pos
            endPos = self.parent.getRelativePoint(render, m_pos)
            
            # Adjust Z coord if needed
            if self._movingUp:
                self._zPos += 0.1
            elif self._movingDown:
                self._zPos -= 0.1
            endPos.setZ(self._zPos)
            
            # Check if we're trying to move too far, if not update pos
            dist = math.sqrt(endPos.getX()**2 + endPos.getY()**2 + 2*(endPos.getZ()**2))
            if dist <= self.moveRad:
                self._moveLine.setVertex(1, endPos)
                self._moveFootCircleNP.setPos(endPos)
                #self._currentPos = self.parent.getRelativePoint(self.parent, endPos)
                #print("endPos=%s"%endPos)
                #print("myRelPos=%s"%self._currentPos)
                self._currentPos = endPos
                
        return Task.cont
        
    def getMouseXY(self):
        # NOTE - this returns the mouse pos in the ships coord sys
        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()
            pos3d = Point3()
            nearPoint = Point3()
            farPoint = Point3()
            base.camLens.extrude(mpos, nearPoint, farPoint)
            if self.plane.intersectsLine(pos3d,
                render.getRelativePoint(camera, nearPoint),
                render.getRelativePoint(camera, farPoint)):
                    return pos3d
        return None
        
    def getPosition(self):
        return self._currentPos
    
    def startDrawing(self):
        self._np.reparentTo(self.parent)
        taskMgr.add(self.updateMovePos, 'Movement Indicator Update Task')
        
    def stopDrawing(self):
        taskMgr.remove('Movement Indicator Update Task')
        self._np.detachNode()

class Square(object):
    #Draws a square from lower left (x1, y2, z1) to upper right (x2, y2, z2)
    def __init__(self, parent, p1, p2, color):
        self.parent = parent
        self.x1 = p1.getX()
        self.y1 = p1.getY()
        self.z1 = p1.getZ()
        self.x2 = p2.getX()
        self.y2 = p2.getY()
        self.z2 = p2.getZ()
        
        self.r = color.getX()
        self.g = color.getY()
        self.b = color.getZ()
        self.a = color.getW()
        
        self.draw()
    
    def draw(self):
        format=GeomVertexFormat.getV3n3cpt2()
        vdata=GeomVertexData('square', format, Geom.UHStatic)
        
        vertex=GeomVertexWriter(vdata, 'vertex')
        normal=GeomVertexWriter(vdata, 'normal')
        color=GeomVertexWriter(vdata, 'color')
        texcoord=GeomVertexWriter(vdata, 'texcoord')
        
        #make sure we draw the sqaure in the right plane
        #if x1!=x2:
        vertex.addData3f(self.x1, self.y1, self.z1)
        vertex.addData3f(self.x2, self.y1, self.z1)
        vertex.addData3f(self.x2, self.y2, self.z2)
        vertex.addData3f(self.x1, self.y2, self.z2)
    
        normal.addData3f(Vec3(2*self.x1-1, 2*self.y1-1, 2*self.z1-1).normalize())
        normal.addData3f(Vec3(2*self.x2-1, 2*self.y1-1, 2*self.z1-1).normalize())
        normal.addData3f(Vec3(2*self.x2-1, 2*self.y2-1, 2*self.z2-1).normalize())
        normal.addData3f(Vec3(2*self.x1-1, 2*self.y2-1, 2*self.z2-1).normalize())
        
        #adding different colors to the vertex for visibility
        color.addData4f(self.r, self.g, self.b, self.a)
        color.addData4f(self.r, self.g, self.b, self.a)
        color.addData4f(self.r, self.g, self.b, self.a)
        color.addData4f(self.r, self.g, self.b, self.a)
        
        texcoord.addData2f(0.0, 1.0)
        texcoord.addData2f(0.0, 0.0)
        texcoord.addData2f(1.0, 0.0)
        texcoord.addData2f(1.0, 1.0)
    
        #quads arent directly supported by the Geom interface
        #you might be interested in the CardMaker class if you are
        #interested in rectangle though
        tri1=GeomTriangles(Geom.UHStatic)
        tri2=GeomTriangles(Geom.UHStatic)
        
        tri1.addVertex(0)
        tri1.addVertex(1)
        tri1.addVertex(3)
        
        tri2.addConsecutiveVertices(1,3)
        
        tri1.closePrimitive()
        tri2.closePrimitive()
        
        square=Geom(vdata)
        square.addPrimitive(tri1)
        square.addPrimitive(tri2)
        #square.setIntoCollideMask(BitMask32.bit(1))
        
        self.squareNP = NodePath(GeomNode('square gnode')) 
        self.squareNP.node().addGeom(square)
        self.squareNP.setTransparency(1) 
        self.squareNP.setAlphaScale(.5) 
        self.squareNP.setTwoSided(True)
        #squareNP.setCollideMask(BitMask32.bit(1))
        self.squareNP.reparentTo(self.parent)
        
        return self.squareNP