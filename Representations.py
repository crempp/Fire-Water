
# Python imports
import math

# Panda imports
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import AntialiasAttrib
from pandac.PandaModules import BitMask32
from pandac.PandaModules import GraphicsOutput
from pandac.PandaModules import NodePath
from pandac.PandaModules import OrthographicLens
from pandac.PandaModules import PNMImage
from pandac.PandaModules import Point3
from pandac.PandaModules import Point2
from pandac.PandaModules import PointLight
from pandac.PandaModules import Texture
from pandac.PandaModules import TextureStage
from pandac.PandaModules import TransparencyAttrib
from pandac.PandaModules import VBase3D
from pandac.PandaModules import Vec2
from pandac.PandaModules import Vec3
from pandac.PandaModules import Vec4
from pandac.PandaModules import TextNode
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText

# Game imports
import Event

class Representation(object):
    '''An abstract class that represents any logical entity in the game.'''
    pos = Vec3(0, 0, 0)
    hpr = Vec3(0, 0, 0)
    model = None
    tag = ""
    entity = None
    foot    = 10
    aaLevel = 2
    
    def __init__(self,  pos=None,  hpr=None,  tag="", model='', parent=render):
        if pos != None:
            self.pos = pos
        if hpr != None:
            self.hpr = hpr
        if tag != "":
            self.tag = tag
        self.aaLevel = 16
        self.parent = parent
        self.baseNode = self.parent.attachNewNode(self.__class__.__name__)
        self.baseNode.setPos(self.pos)
        
    def getPos(self):
        return self.pos
        
    def setModel(self, model):
        self.model = model
        
    def setPos(self, pos):
        self.pos = pos
        
    def setHpr(self, hpr):
        self.hpr = hpr
        
    def getTag(self):
        return self.tag
        
    def select(self):
        '''Must be subclassed'''
        pass
        
    def __repr__(self):
        return "<Rep: " + self.tag + ", pos=" + str(self.pos) + ">"
    
class RepShip(Representation):
    _selectindicator = None
    _movecursor = None
    
    _pitchInc   = 1
    _headingInc = 1
    _powerInc   = 1
    
    _gunPitch   = 0
    _gunHeading = 0
    _gunPower   = 0
    
    _pitchUpStateOn      = False
    _pitchDownStateOn    = False
    _headingLeftStateOn  = False
    _headingRightStateOn = False
    _powerUpStateOn      = False
    _powerDownStateOn    = False
    
    def __init__(self, pos=None,  hpr=None,  tag="", model='', parent=render):
        Representation.__init__(self, pos,  hpr, tag, model, parent)
        
        Event.Dispatcher().register(self, 'E_Key_ArrowUp-down',   self.setPitchUpOn)
        Event.Dispatcher().register(self, 'E_Key_ArrowUp-up',     self.setPitchUpOff)
        
        Event.Dispatcher().register(self, 'E_Key_ArrowDown-down',  self.setPitchDownOn)
        Event.Dispatcher().register(self, 'E_Key_ArrowDown-up',    self.setPitchDownOff)
        
        Event.Dispatcher().register(self, 'E_Key_ArrowLeft-down',  self.setHeadingLeftOn)
        Event.Dispatcher().register(self, 'E_Key_ArrowLeft-up',    self.setHeadingLeftOff)
        
        Event.Dispatcher().register(self, 'E_Key_ArrowRight-down', self.setHeadingRightOn)
        Event.Dispatcher().register(self, 'E_Key_ArrowRight-up',   self.setHeadingRightOff)
        
        Event.Dispatcher().register(self, 'E_Key_PageUp-down',     self.setPowerUpOn)
        Event.Dispatcher().register(self, 'E_Key_PageUp-up',       self.setPowerUpOff)
        
        Event.Dispatcher().register(self, 'E_Key_PageDown-down',   self.setPowerDownOn)
        Event.Dispatcher().register(self, 'E_Key_PageDown-up',     self.setPowerDownOff)
        
        taskMgr.add(self.setGun, 'Gun Update Task')
        self.showInfo(init=True)
        
    def showInfo(self, init=False):
        if (not init):
            self._pitchText.destroy()
            self._headingText.destroy()
            self._powerText.destroy()
        
        self._pitchText   = OnscreenText(text = 'Pitch: %s'%self._gunPitch,
                                         pos = (-1.30, 0.95),
                                         scale = 0.05,
                                         align = TextNode.ALeft)
        self._headingText = OnscreenText(text = 'Heading: %s'%self._gunHeading,
                                         pos = (-1.30, 0.87),
                                         scale = 0.05,
                                         align = TextNode.ALeft)
        self._powerText   = OnscreenText(text = 'Power: %s'%self._gunPower,
                                         pos = (-1.30, 0.79),
                                         scale = 0.05,
                                         align = TextNode.ALeft)
        
    def selectMove(self):
        LOG.debug("[RepShip] Drawing move selector")
        # Draw movement radii
        self._selectindicator = GeomObjects.SelectionIndicator(self.model, size=self.foot)
        self._movecursor   = GeomObjects.MoveCursor(self.model, self.entity, foot=self.foot)
        
    def unselectMove(self):
        if self._selectindicator is not None:
            self._selectindicator.removeNode()
        if self._movecursor is not None:
            self._movecursor.removeNode()
        del(self._selectindicator)
        del(self._movecursor)
        
    def selectAttack(self):
        self._attackcursor = GeomObjects.AttackCursor(self.model, self.entity, foot=self.foot)
        
    def unselectAttack(self):
        if self._attackcursor is not None:
            self._attackcursor.removeNode()
        del(self._attackcursor)
        
    def move(self, pos):
        # Get direction to head
        currentHpr = self.model.getHpr()
        self.model.lookAt(pos.getX(), pos.getY(), pos.getZ())
        targetHpr = self.model.getHpr()
        self.model.setHpr(currentHpr) 
        
        # Rotate to heading
        rot = LerpHprInterval(self.model, duration=1, hpr = targetHpr,
                other = None, blendType = 'easeInOut', bakeInStart = 1,
                fluid = 0, name = None)
        # Move
        mov = LerpPosInterval(self.model, duration=3,   pos = pos, #Vec3(10, 0, 0),
                startPos = None, other = None, blendType = 'easeInOut',
                bakeInStart = 1, fluid = 0, name = None)
        # Level off (pitch = 0)
        lev = LerpHprInterval(self.model,   duration=0.7, hpr = Vec3(targetHpr.getX(), 0, 0),
                other = None, blendType = 'easeInOut', bakeInStart = 1,
                fluid = 0, name = None)
        moveSequence=Sequence(Func(self.fireEngines), rot, mov, lev, Func(self.killEngines))
        moveSequence.start()
        self.pos = pos
        
    def setGun(self, task):
        # Only run once every 30 frames
        if ((task.frame % 30) == 0):
            updated = False
            if self._pitchUpStateOn:
                self._gunPitch = min(90, self._gunPitch + self._pitchInc)
                updated = True
            elif self._pitchDownStateOn:
                self._gunPitch = max(0, self._gunPitch - self._pitchInc)
                updated = True
            
            if self._headingLeftStateOn:
                self._gunHeading = (self._gunHeading + self._headingInc) % 360
                updated = True
            elif self._headingRightStateOn:
                self._gunHeading = (self._gunHeading - self._headingInc) % 360
                updated = True
            
            if self._powerUpStateOn:
                self._gunPower = min(self._power, self._gunPower + self._powerInc)
                updated = True
            elif self._powerDownStateOn:
                self._gunPower = max(0, self._gunPower - self._powerInc)
                updated = True
            
            if updated:
                self.showInfo()
                print("(%s,%s,%s)"%(self._gunPitch, self._gunHeading, self._gunPower))
        
        return task.cont
            
    def setPitchUpOn(self, event):
        self._pitchUpStateOn = True
    def setPitchUpOff(self, event):
        self._pitchUpStateOn = False
        
    def setPitchDownOn(self, event):
        self._pitchDownStateOn = True
    def setPitchDownOff(self, event):
        self._pitchDownStateOn = False
        
    def setHeadingLeftOn(self, event):
        self._headingLeftStateOn = True
    def setHeadingLeftOff(self, event):
        self._headingLeftStateOn = False
    
    def setHeadingRightOn(self, event):
        self._headingRightStateOn = True
    def setHeadingRightOff(self, event):
        self._headingRightStateOn = False
    
    def setPowerUpOn(self, event):
        self._powerUpStateOn = True
    def setPowerUpOff(self, event):
        self._powerUpStateOn = False
        
    def setPowerDownOn(self, event):
        self._powerDownStateOn = True
    def setPowerDownOff(self, event):
        self._powerDownStateOn = False
        
class BattleShip(RepShip):
    _power = 100
    
    def __init__(self, pos=None,  hpr=None,  tag="", model='', parent=render):
        RepShip.__init__(self, pos, hpr, tag, model, parent)
        
        self.model = loader.loadModelCopy("assets/models/ship_01.x")
        #self.model = loader.loadModelCopy("assets/models/heavy_cruiser.egg")
        self.model.setScale(0.5)
        self.model.setPos(self.pos)
        self.model.setHpr(self.hpr)
        self.model.setTag('SelectorTag', self.tag)
        if self.aaLevel > 0:
            self.model.setAntialias(AntialiasAttrib.MMultisample, self.aaLevel)
        self.model.reparentTo(self.baseNode)
        print (self.baseNode)
        print (self.model)
        #TESTING
        self.model.setColor(0.0, 0.3, 0.3)
        
    def fireRockets(self, target):
        print("FIRING ROCKETS!!!")
        
        self.modelRocket = loader.loadModelCopy("data/models/rocket.egg")
        self.modelRocket.setScale(1)
        self.modelRocket.setPos(0, 0, 0)
        
        currentHpr = self.model.getHpr()
        self.modelRocket.setHpr(currentHpr)
        self.modelRocket.reparentTo(self.model)
        targetPos = self.model.getRelativePoint(render, target)
        
        #targetHpr = self.model.getHpr()
        #self.model.setHpr(currentHpr) 
        mov = LerpPosInterval(self.modelRocket, duration=3, pos = targetPos, #Vec3(10, 0, 0),
                startPos = None, other = None, blendType = 'easeInOut',
                bakeInStart = 1, fluid = 0, name = None)
        moveSequence=Sequence(mov, Func(self.modelRocket.removeNode))
        moveSequence.start()
        