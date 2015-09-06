# Python imports
from __future__ import division
import math

# Panda imports
import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import AntialiasAttrib
from pandac.PandaModules import BillboardEffect
from pandac.PandaModules import DepthTestAttrib
from pandac.PandaModules import Geom
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
from pandac.PandaModules import MeshDrawer

class World(DirectObject):
    _color      = Vec4(0.3, 0.3, 0.8, 1)
    
    def __init__(self):
        
        s = Square(render, Point3(0,0,0), Point3(10,10,10), self._color)

class Square(object):
    #drawSquare
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

w = World()
run()