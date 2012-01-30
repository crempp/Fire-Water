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
        
        self.gameMgr = GameManager()
        
        guiMgr = GuiManager()
        
        ########################################################################
        w = Water(boardNP)
        
        self.gameMgr.addPlayer(1, "Player 1")
        self.gameMgr.addPlayer(2, "Player 2")
        
        s1 = BattleShip(parent=w.baseNode, pos=Vec3(50, 0, 0))
        s2 = BattleShip(parent=w.baseNode, pos=Vec3(-30, 10, 0))
        
        self.gameMgr.addPlayerUnit(1, s1)
        self.gameMgr.addPlayerUnit(2, s2)
        
        # move this to dispatcher
        s1.setGame(self)
        s2.setGame(self)
        
        # move this to dispatcher
        s1.startTurn()
        
        self.gamePieces = [s1, s2]
        
        ########################################################################        
        
        # Camera
        c = CameraManager()
        c.startCamera()
        c.setTarget(s1)
        
        
        # Debugging
        #self.coordDebug3D()
        #self.coordDebug3D(s1.baseNode)
        #self.coordDebug2D()
        #print(s1.pos)
        #print(s1.model.getPos())
        
    
    
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
        

class GameManager(object):
    _players = {}
    
    _activePlayer = None
    _activeUnit   = 0
    
    _hitRadius = 3
    
    def __init__(self):
        Event.Dispatcher().register(self, 'E_Unit_EndTurn', self._nextTurn)
        Event.Dispatcher().register(self, 'E_HitCheck',     self._checkHit)
        
    def addPlayer(self, id, playerName):
        
        if (len(self._players) == 0):
            self._activePlayer = id
        
        self._players[id] = {'name':  playerName,
                             'units': []}
        
    def addPlayerUnit(self, id, unit):
        self._players[id]['units'].append(unit)
    
    def _checkHit(self, event):
        shooter = event.source
        hitPos  = event.data
        print(self._players)
        for id, p in self._players.items():
            print("2")
            for u in p['units']:
                hitVec = hitPos - u.pos
                dist   = hitVec.length()
                
                if (dist < self._hitRadius):
                    # Run the hit sequence
                    hitSequence=Sequence(Func(u.explode),
                                         Func(u.doDamage, dist),
                                         Func(self._nextTurn))
                    hitSequence.start()
    
    def _nextTurn(self, event):
        currPlayer = self._players[self._activePlayer]
        # are there any more units left for the current player?
        if (self._activeUnit < len(currPlayer['units']) - 1):
            # next unit same player
            LOG.debug("Switching from p%s u%s to u%s"%(self._activePlayer, self._activeUnit, self._activeUnit + 1))
            
            currPlayer['units'][self._activeUnit].endTurn()
            self._activeUnit += 1
            currPlayer['units'][self._activeUnit].startTurn()
        else:
            # lookup next player
            numPlayers = len(self._players)
            
            playerIDList      = self._players.keys()
            playerIDList.sort()
            print(playerIDList)
            activePlayerIndex = playerIDList.index(self._activePlayer)
            nextPlayerIndex   = (activePlayerIndex + 1) % len(playerIDList)
            nextPlayerID      = playerIDList[nextPlayerIndex]
            
            nextPlayer = self._players[nextPlayerID]
            
            self._activePlayer = nextPlayerID
            currPlayer['units'][self._activeUnit].endTurn()
            self._activeUnit = 0
            nextPlayer['units'][self._activeUnit].startTurn()
        
        e = Event.Event('E_NewCameraTarget',
                        self,
                        data=self._players[self._activePlayer]['units'][self._activeUnit])
        Event.Dispatcher().broadcast(e)

class GuiManager(object):
    _playerText  = None
    _pitchText   = None
    _headingText = None
    _powerText   = None
    _damageText  = None
    
    
    def __init__(self):
        Event.Dispatcher().register(self, 'E_UnitInfoUpdate',   self.updateShipInfo)
        Event.Dispatcher().register(self, 'E_TurnInfoUpdate',   self.updateShipInfo)
        
        self.updateShipInfo(None, True)
        self.updateTurnInfo(None, True)
    
    def updateTurnInfo(self, event, init=False):
        self._currPlayerText   = OnscreenText(text = 'Player 1',
                                              pos = (1.00, 0.95),
                                              scale = 0.05,
                                              align = TextNode.ALeft)
        self._turnNomText      = OnscreenText(text = 'Turn 1',
                                              pos = (1.00, 0.87),
                                              scale = 0.05,
                                              align = TextNode.ALeft)
    
    def updateShipInfo(self, event, init=False):
        if (not init):
            self._pitchText.destroy()
            self._headingText.destroy()
            self._powerText.destroy()
            self._damageText.destroy()
            
            pitchNum   = event.source.gunPitch
            headingNum = event.source.gunHeading
            powerNum   = event.source.gunPower
            damageNum  = event.source.damage
            totalDamageNum = event.source.damageLimit
        else:
            pitchNum   = '-'
            headingNum = '-'
            powerNum   = '-'
            damageNum  = '-'
            totalDamageNum = '-'
        
        self._pitchText   = OnscreenText(text = 'Pitch: %s'%pitchNum,
                                         pos = (-1.30, 0.95),
                                         scale = 0.05,
                                         align = TextNode.ALeft)
        self._headingText = OnscreenText(text = 'Heading: %s'%headingNum,
                                         pos = (-1.30, 0.87),
                                         scale = 0.05,
                                         align = TextNode.ALeft)
        self._powerText   = OnscreenText(text = 'Power: %s'%powerNum,
                                         pos = (-1.30, 0.79),
                                         scale = 0.05,
                                         align = TextNode.ALeft)
        self._damageText  = OnscreenText(text = 'Damage: %s/%s'%(damageNum,totalDamageNum),
                                         pos = (-1.30, 0.71),
                                         scale = 0.05,
                                         align = TextNode.ALeft)
        
w = World()
run()