import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
#from panda3d.core import CollisionTraverser,CollisionNode
#from panda3d.core import CollisionHandlerQueue,CollisionRay
#from panda3d.core import Filename,AmbientLight,DirectionalLight
#from panda3d.core import PandaNode,NodePath,Camera,TextNode
#from panda3d.core import Vec3,Vec4,BitMask32
#from direct.gui.OnscreenText import OnscreenText
#from direct.actor.Actor import Actor
from pandac.PandaModules import NodePath
from pandac.PandaModules import Vec3

from direct.gui.OnscreenText import OnscreenText
from pandac.PandaModules import PandaNode,Camera,TextNode
from direct.gui.DirectGui import *

#import random, sys, os, math

from Water import Water
from Representations import BattleShip

import Controller
import Event

from Log import LogConsole
from CameraMgr import CameraManager

class World(DirectObject):
    hitRadius = 1
    
    def __init__(self):
        # Setup logger
        import __builtin__
        __builtin__.LOG = LogConsole()
        
        # Initialize event dispatcher
        self._dispatcher = Event.Dispatcher()        
        
        # Setup controls
        self.keyboardcontroller = Controller.KeyboardController()
        self.mousecontroller = Controller.MouseController()
        
        # Build game board
        boardNP = NodePath("Game Board Parent")
        boardNP.reparentTo(render)
        
        self.gamePieces = []
        
        ########################################################################
        w = Water(boardNP)
        
        s1 = BattleShip(parent=w.baseNode, pos=Vec3(25, 0, 0))
        s2 = BattleShip(parent=w.baseNode, pos=Vec3(-25, 0, 0))
        
        s1.setGame(self)
        s2.setGame(self)
        
        s1.activate()
        
        self.gamePieces = [s1, s2]
        
        ########################################################################        
        
        # Camera
        c = CameraManager()
        c.startCamera()
        
        c.setTarget(s1)
        
        self.coordDebug()
        
    def checkHit(self, pos):
        for s in self.gamePieces:
            hitVec = pos - s.pos
            dist   = hitVec.length()
            print("hit  = %s"%pos)
            print("ship = %s"%s.pos)
            print("dist = %s"%dist)
    
    # Coord debug functions
    # From http://code.google.com/p/python-panda3d-examples/wiki/PandaCoords
    def coordDebug(self):
        for i in range(0,51):
            self.printText("X", "|", (1,0,0)).setPos(i,0,0) 
        
        for i in range(0,51):
            self.printText("Y", "|", (0,1,0)).setPos(0,i,0)  
                
        for i in range(0,51):
            self.printText("Z", "-", (0,0,1)).setPos(0,0,i) 
        
        self.printText("XL", "X", (0,0,0)).setPos(11.5,0,0) 
        self.printText("YL", "Y", (0,0,0)).setPos(1,10,0) 
        self.printText("YL", "Z", (0,0,0)).setPos(1,0,10) 
        self.printText("OL", "@", (0,0,0)).setPos(0,0,0) 
        
        OnscreenText(text = '(0 , 0)', pos = (.1, .05), scale = 0, fg=(1,1,1,1))
        for i in range(-20,20):
            OnscreenText(text = '.', pos = (0, i/float(10)), scale = 0, fg=(1,1,1,1))
        for i in range(-20,20):
            OnscreenText(text = '.', pos = (i/float(10), 0), scale = 0, fg=(1,1,1,1))
            
        OnscreenText(text = 'X', pos = (1.3, .1), scale = 0, fg=(1,1,1,1))
        OnscreenText(text = 'Y', pos = (.1, .9), scale = 0, fg=(1,1,1,1))
        
        OnscreenText(text="Panda 2D/3D: Coordinate System", style=1,  fg=(1,1,1,1), pos=(0.8,-0.95), scale = .07)
        
        OnscreenText(text="Notes:", style=1,  fg=(1,1,1,1), pos=(0.3,0.8), scale = .07)
        OnscreenText(text="- Each dot represents 0.10 units", style=1,  fg=(1,1,1,1), pos=(0.64,0.7), scale = .07)
        OnscreenText(text="- Each dash represents 1 unit", style=1,  fg=(1,1,1,1), pos=(0.6,0.6), scale = .07)
              
        #base.disableMouse()   
        
    def printText(self, name, message, color): 
        text = TextNode(name) # create a TextNode. Note that 'name' is not the text, rather it is a name that identifies the object.
        text.setText(message) # Here we set the text of the TextNode
        x,y,z = color # break apart the color tuple
        text.setTextColor(x,y,z, 1) # Set the text color from the color tuple
    
        text3d = NodePath(text) # Here we create a NodePath from the TextNode, so that we can manipulate it 'in world'
        text3d.reparentTo(render) # This is important. We reparent the text NodePath to the 'render' tree. 
        # The render tree contains what is going to be rendered into the 3D WORLD. 
        # If we reparented it to 'render2d' instead, it would appear in the 2D WORLD. 
        # The 2D WORLD, from the documentation, is as if someone had written on your computer screen.
        return text3d # return the NodePath for further use
        
        
w = World()
run()