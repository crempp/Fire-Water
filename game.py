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

#import random, sys, os, math

from Water import Water
from Representations import BattleShip

import Controller
import Event

from Log import LogConsole
from CameraMgr import CameraManager

class World(DirectObject):

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
        
        ########################################################################
        w = Water(boardNP)
        
        s1 = BattleShip(parent=w.baseNode, pos=(25, 0, 0))
        s2 = BattleShip(parent=w.baseNode, pos=(-25, 0, 0))
        
        s1.activate()
        
        ########################################################################        
        
        # Camera
        c = CameraManager()
        c.startCamera()
        
        c.setTarget(s1)
        
w = World()
run()