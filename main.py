import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import NodePath
from pandac.PandaModules import Vec3

from direct.gui.OnscreenText import OnscreenText
from pandac.PandaModules import PandaNode,Camera,TextNode
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *

from Water import Water
from Representations import BattleShip

import Controller
import Event

from Log import LogConsole
from CameraMgr import CameraManager

class World(DirectObject):
    hitRadius = 3
    
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
        __builtin__.boardNP = NodePath("Game Board Parent")
        boardNP.reparentTo(render)
        
        self.gamePieces = []
        
        ########################################################################
        w = Water(boardNP)
        
        s1 = BattleShip(parent=w.baseNode, pos=Vec3(50, 0, 0))
        s2 = BattleShip(parent=w.baseNode, pos=Vec3(-30, 10, 0))
        
        s1.setGame(self)
        s2.setGame(self)
        
        s1.activate()
        
        self.gamePieces = [s1, s2]
        
        ########################################################################        
        
        # Camera
        c = CameraManager()
        c.startCamera()
        c.setTarget(s1)
        
        # Debugging
        self.coordDebug3D()
        self.coordDebug3D(s1.baseNode)
        #self.coordDebug2D()
        #print(s1.pos)
        #print(s1.model.getPos())
        
    def checkHit(self, pos):
        for s in self.gamePieces:
            hitVec = pos - s.pos
            dist   = hitVec.length()
            
            if (dist < self.hitRadius):
                LOG.debug("Hit!!!!!!!!!!!!")
                hitSequence=Sequence(Func(s.explode), Func(s.doDamage, dist))
                hitSequence.start()
            
            LOG.debug("hit  = %s"%pos)
            LOG.debug("ship = %s"%s.pos)
            LOG.debug("dist = %s"%dist)
    
    # Coord debug functions
    # From http://code.google.com/p/python-panda3d-examples/wiki/PandaCoords
    def coordDebug3D(self, parent=render):
        for i in range(0,51):
            self.printText("X", "|", (1,0,0), parent).setPos(i,0,0) 
        
        for i in range(0,51):
            self.printText("Y", "|", (0,1,0), parent).setPos(0,i,0)  
                
        for i in range(0,51):
            self.printText("Z", "-", (0,0,1), parent).setPos(0,0,i) 
        
        self.printText("XL", "X", (0,0,0), parent).setPos(11.5,0,0) 
        self.printText("YL", "Y", (0,0,0), parent).setPos(1,10,0) 
        self.printText("YL", "Z", (0,0,0), parent).setPos(1,0,10) 
        self.printText("OL", "@", (0,0,0), parent).setPos(0,0,0)
        
    def coordDebug2D(self):
        OnscreenText(text = '(0 , 0)', pos = (.1, .05), scale = 0, fg=(1,1,1,1))
        for i in range(-20,20):
            OnscreenText(text = '.', pos = (0, i/float(10)), scale = 0, fg=(1,1,1,1))
        for i in range(-20,20):
            OnscreenText(text = '.', pos = (i/float(10), 0), scale = 0, fg=(1,1,1,1))
            
        OnscreenText(text = 'X', pos = (1.3, .1), scale = 0, fg=(1,1,1,1))
        OnscreenText(text = 'Y', pos = (.1, .9), scale = 0, fg=(1,1,1,1))
        
    def printText(self, name, message, color, parent=render): 
        text = TextNode(name) # create a TextNode. Note that 'name' is not the text, rather it is a name that identifies the object.
        text.setText(message) # Here we set the text of the TextNode
        x,y,z = color # break apart the color tuple
        text.setTextColor(x,y,z, 1) # Set the text color from the color tuple
    
        text3d = NodePath(text) # Here we create a NodePath from the TextNode, so that we can manipulate it 'in world'
        text3d.reparentTo(parent)
        return text3d # return the NodePath for further use
        

class TurnManager(object):
    _players = {}
    def __init__(self, players):
        Event.Dispatcher().register(self, 'E_Player_EndTurn',   self._nextTurn)
        
    def addPlayer(id, playerName):
        pass
    
    def _nextTurn(self, event):
        pass



w = World()
run()