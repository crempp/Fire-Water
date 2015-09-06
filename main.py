import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import NodePath
from pandac.PandaModules import Vec3

from direct.gui.OnscreenText import OnscreenText
from pandac.PandaModules import PandaNode,Camera,TextNode
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *

# For lights \/
from panda3d.core import AmbientLight,DirectionalLight
from pandac.PandaModules import Vec4

# For glow
from direct.filter.CommonFilters import CommonFilters
from panda3d.core import Filename,Buffer,Shader
from panda3d.core import LightRampAttrib
from panda3d.core import ColorBlendAttrib

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
        
        s1 = BattleShip(parent=render, pos=Vec3(50, 0, 0))
        s2 = BattleShip(parent=render, pos=Vec3(-30, 10, 0))
        
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
        
        ####LIGHTS#########################################################
        dlight = DirectionalLight('dlight')
        alight = AmbientLight('alight')
        dlnp = render.attachNewNode(dlight) 
        alnp = render.attachNewNode(alight)
        dlight.setColor(Vec4(0.5, 0.5, 0.7, 1))
        alight.setColor(Vec4(0.7, 0.7, 0.7, 1))
        dlnp.setHpr(0, -60, 0) 
        render.setLight(dlnp)
        render.setLight(alnp)
        
        # Glow test
        #glowShader=loader.loadShader("shaders/glowShader.sha")
        #
        ## create the glow buffer. This buffer renders like a normal scene,
        ## except that only the glowing materials should show up nonblack.
        #glowBuffer=base.win.makeTextureBuffer("Glow scene", 512, 512)
        #glowBuffer.setSort(-3)
        #glowBuffer.setClearColor(Vec4(0,0,0,1))
        #
        ## We have to attach a camera to the glow buffer. The glow camera
        ## must have the same frustum as the main camera. As long as the aspect
        ## ratios match, the rest will take care of itself.
        #glowCamera=base.makeCamera(glowBuffer, lens=base.cam.node().getLens())
        #
        ## Tell the glow camera to use the glow shader
        #tempnode = NodePath(PandaNode("temp node"))
        #tempnode.setShader(glowShader)
        #glowCamera.node().setInitialState(tempnode.getState())
        #
        ## set up the pipeline: from glow scene to blur x to blur y to main window.
        #blurXBuffer=self.makeFilterBuffer(glowBuffer,  "Blur X", -2, "shaders/XBlurShader.sha")
        #blurYBuffer=self.makeFilterBuffer(blurXBuffer, "Blur Y", -1, "shaders/YBlurShader.sha")
        #self.finalcard = blurYBuffer.getTextureCard()
        #self.finalcard.reparentTo(render2d)
        #self.finalcard.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
        #
        #base.bufferViewer.setPosition("llcorner")
        #base.bufferViewer.setLayout("hline")
        #base.bufferViewer.setCardSize(0.652,0)
        #base.bufferViewer.toggleEnable
        
        # Toon test
        #self.separation = 0.5
        ## This shader's job is to render the model with discrete lighting
        ## levels.  The lighting calculations built into the shader assume
        ## a single nonattenuating point light.
        #
        #tempnode = NodePath(PandaNode("temp node"))
        #tempnode.setShader(loader.loadShader("shaders/lightingGen.sha"))
        #base.cam.node().setInitialState(tempnode.getState())
        #
        ## This is the object that represents the single "light", as far
        ## the shader is concerned.  It's not a real Panda3D LightNode, but
        ## the shader doesn't care about that.
        #
        #light = render.attachNewNode("light")
        #light.setPos(30,-50,0)
        #        
        ## this call puts the light's nodepath into the render state.
        ## this enables the shader to access this light by name.
        #
        #render.setShaderInput("light", light)
        #
        ## The "normals buffer" will contain a picture of the model colorized
        ## so that the color of the model is a representation of the model's
        ## normal at that point.
        #
        #normalsBuffer=base.win.makeTextureBuffer("normalsBuffer", 0, 0)
        #normalsBuffer.setClearColor(Vec4(0.5,0.5,0.5,1))
        #self.normalsBuffer=normalsBuffer
        #normalsCamera=base.makeCamera(normalsBuffer, lens=base.cam.node().getLens())
        #normalsCamera.node().setScene(render)
        #tempnode = NodePath(PandaNode("temp node"))
        #tempnode.setShader(loader.loadShader("shaders/normalGen.sha"))
        #normalsCamera.node().setInitialState(tempnode.getState())
        #
        ##what we actually do to put edges on screen is apply them as a texture to 
        ##a transparent screen-fitted card
        #
        #drawnScene=normalsBuffer.getTextureCard()
        #drawnScene.setTransparency(1)
        #drawnScene.setColor(1,1,1,0)
        #drawnScene.reparentTo(render2d)
        #self.drawnScene = drawnScene
        #
        ## this shader accepts, as input, the picture from the normals buffer.
        ## it compares each adjacent pixel, looking for discontinuities.
        ## wherever a discontinuity exists, it emits black ink.
        #        
        #self.separation = 0.001
        #self.cutoff = 0.3
        #inkGen = loader.loadShader("shaders/inkGen.sha")
        #drawnScene.setShader(inkGen)
        #drawnScene.setShaderInput("separation", Vec4(self.separation,0,self.separation,0));
        #drawnScene.setShaderInput("cutoff", Vec4(self.cutoff,self.cutoff,self.cutoff,self.cutoff));
        
        
        ### GO GO GO #####################################
        self.gameMgr.startGame()
        # Debugging
        #self.coordDebug3D()
        #self.coordDebug3D(s1.baseNode)
        #self.coordDebug2D()
        #print(s1.pos)
        #print(s1.model.getPos())
        
    def makeFilterBuffer(self, srcbuffer, name, sort, prog):
        blurBuffer=base.win.makeTextureBuffer(name, 512, 512)
        blurBuffer.setSort(sort)
        blurBuffer.setClearColor(Vec4(0,0,0,1))
        blurCamera=base.makeCamera2d(blurBuffer)
        blurScene=NodePath("new Scene")
        blurCamera.node().setScene(blurScene)
        shader = loader.loadShader(prog)
        card = srcbuffer.getTextureCard()
        card.reparentTo(blurScene)
        card.setShader(shader)
        return blurBuffer
    
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
    
    turnCount = 0
    
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

    def startGame(self):
        self._nextTurn(None)
    
    def getCurrentPlayer(self):
        return self._players[self._activePlayer]
    
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
        if (event is not None):
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
                #print(playerIDList)
                activePlayerIndex = playerIDList.index(self._activePlayer)
                nextPlayerIndex   = (activePlayerIndex + 1) % len(playerIDList)
                nextPlayerID      = playerIDList[nextPlayerIndex]
                
                nextPlayer = self._players[nextPlayerID]
                
                self._activePlayer = nextPlayerID
                currPlayer['units'][self._activeUnit].endTurn()
                self._activeUnit = 0
                nextPlayer['units'][self._activeUnit].startTurn()
                
                turnCount += 1
        
        e = Event.Event('E_NewCameraTarget',
                        self,
                        data=self._players[self._activePlayer]['units'][self._activeUnit])
        Event.Dispatcher().broadcast(e)
        e = Event.Event('E_TurnInfoUpdate',
                        self,
                        data=self._players[self._activePlayer]['units'][self._activeUnit])
        Event.Dispatcher().broadcast(e)

class GuiManager(object):
    _playerText     = None
    _pitchText      = None
    _headingText    = None
    _powerText      = None
    _damageText     = None
    _currPlayerText = None
    _turnNumText    = None
    _unitTypeText   = None
    
    def __init__(self):
        Event.Dispatcher().register(self, 'E_UnitInfoUpdate',   self.updateShipInfo)
        Event.Dispatcher().register(self, 'E_TurnInfoUpdate',   self.updateTurnInfo)
        
        self.updateShipInfo(None, True)
        self.updateTurnInfo(None, True)
    
    def updateTurnInfo(self, event, init=False):
        if (not init):
            self._currPlayerText.destroy()
            self._turnNumText.destroy()
            self._unitTypeText.destroy()
            
            player   = event.source.getCurrentPlayer()['name']
            turnNum  = str(event.source.turnCount)
            unitType = event.data.title
        else:
            player   = '-'
            turnNum  = '-'
            unitType = '-'
        
        self._currPlayerText   = OnscreenText(text = player,
                                              pos = (1.00, 0.95),
                                              scale = 0.05,
                                              align = TextNode.ALeft)
        self._turnNumText      = OnscreenText(text = turnNum,
                                              pos = (1.00, 0.87),
                                              scale = 0.05,
                                              align = TextNode.ALeft)
        self._unitTypeText     = OnscreenText(text = unitType,
                                              pos = (1.00, 0.79),
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