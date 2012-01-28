
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
from pandac.PandaModules import BillboardEffect
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText

# Game imports
import Event
from GeomObjects import MoveCursor, SelectionIndicator

GRAV_ACCEL = 9.80665
RAD_FACTOR = (math.pi / 180)
DEG_FACTOR = (180 / math.pi)

class Representation(object):
    '''An abstract class that represents any logical entity in the game.'''
    pos = Vec3(0, 0, 0)
    hpr = Vec3(0, 0, 0)
    model = None
    tag = ""
    entity = None
    foot    = 10
    aaLevel = 2
    game = None
    
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
        
    def setGame(self, game):
        self.game = game
        
    def __repr__(self):
        return "<Rep: " + self.tag + ", pos=" + str(self.pos) + ">"
    
class RepShip(Representation):
    _active = False
    
    moveRadius = 20
    
    _selectindicator = None
    _movecursor = None

    _damage      = 0
    _damageLimit = 100
    
    _pitchInc   = 1
    _headingInc = 1
    _powerInc   = 1
    
    #_gunPitch   = 45
    #_gunHeading = 0
    #_gunPower   = 50
    _gunPitch   = 45
    _gunHeading = 276
    _gunPower   = 28
    _gunTheta   = 0    
    _gunHeadingTheta =0
    
    _pitchUpStateOn      = False
    _pitchDownStateOn    = False
    _headingLeftStateOn  = False
    _headingRightStateOn = False
    _powerUpStateOn      = False
    _powerDownStateOn    = False
    
    _selectMoveState = False
    _movingState     = False
    
    _mortar = None
    
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
        
        Event.Dispatcher().register(self, 'E_Key_Fire',            self.fire)
        Event.Dispatcher().register(self, 'E_Key_Move',            self.toggleSelectMoveState)
        Event.Dispatcher().register(self, 'E_Mouse_1',             self.move)
        
        taskMgr.add(self.setGun, 'Gun Update Task')
        
        self.showInfo(init=True)
        
    def showInfo(self, init=False):
        if (not init):
            self._pitchText.destroy()
            self._headingText.destroy()
            self._powerText.destroy()
            self._damageText.destroy()
        
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
        self._damageText  = OnscreenText(text = 'Damage: %s'%self._damage,
                                         pos = (-1.30, 0.71),
                                         scale = 0.05,
                                         align = TextNode.ALeft)

    def activate(self):
       self._active = True
       
    def deactivate(self):
       self._active = False 
    
    def toggleSelectMoveState(self, event):
        if self._active and not self._selectMoveState:
            LOG.debug("Move select on")
            self._selectMoveState = True
            self.selectMove()
        elif self._active and self._selectMoveState:
            LOG.debug("Move select off")
            self._selectMoveState = False
            self.unselectMove()
            
    def selectMove(self):
        self._movecursor.startDrawing()
        
    def unselectMove(self):
        self._movecursor.stopDrawing()
    
    def move(self, event):
        if self._active and self._selectMoveState:
            pos = self._movecursor.getPosition()
            myRelPos = render.getRelativePoint(self.baseNode, pos)
            print("myRelPos=%s"%myRelPos)
            
            self._selectMoveState = False
            self.unselectMove()
            
            # Get direction to head
            currentHpr = self.baseNode.getHpr()
            self.baseNode.lookAt(pos.getX(), pos.getY(), pos.getZ())
            targetHpr = self.baseNode.getHpr()
            self.baseNode.setHpr(currentHpr) 
            
            # Rotate to heading
            rot = LerpHprInterval(self.baseNode, duration=1, hpr = targetHpr,
                    other = None, blendType = 'easeInOut', bakeInStart = 1,
                    fluid = 0, name = None)
            # Move
            mov = LerpPosInterval(self.baseNode, duration=3,   pos = myRelPos, #Vec3(10, 0, 0),
                    startPos = None, other = None, blendType = 'easeInOut',
                    bakeInStart = 1, fluid = 0, name = None)
            moveSequence=Sequence(rot, mov)
            moveSequence.start()
            self.pos = pos
        
    def setGun(self, task):
        # Only run once every 15 frames
        if ((task.frame % 15) == 0):
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
        
    def fire(self, event):
        if (self._active):
            self._mortar = loader.loadModel("assets/models/mortar")
            self._mortar.setScale(1)
            self._mortar.setPos(0, 0, 0)
            self._mortar.setHpr(self._gunHeading, self._gunPitch, 0)
            self._mortar.reparentTo(self.baseNode)
            
            self._gunPitchTheta = (math.pi / 2) - (self._gunPitch * RAD_FACTOR)
            self._gunHeadingTheta = self._gunHeading * RAD_FACTOR
            time_of_flight = (2 * math.cos(self._gunPitchTheta) * self._gunPower) / GRAV_ACCEL
            
            duration = time_of_flight / 2
            
            mov = LerpFunc(self.lerpUpdate,
                           fromData=0,
                           toData=time_of_flight,
                           duration=duration,
                           blendType='easeInOut',
                           extraArgs=[],
                           name = "Mortar parabola")
            moveSequence=Sequence(mov, Func(self._checkHit), Func(self._mortar.removeNode))
            moveSequence.start()
        
    def lerpUpdate(self, t):
        # Update the position of the rocket using a parabolic equation for a parabola
        # x(t) = v * cos(theta) * t
        # y(t) = v * sin(theta) * t - (0.5 * g * t^2)
        
        # Calculate the distance of the trajectory - normally x
        d0 = self._gunPower * math.sin(self._gunPitchTheta) * (t - 0.1)
        d  = self._gunPower * math.sin(self._gunPitchTheta) * t
        
        # Split the distance into x and y components
        x = d * math.sin(self._gunHeadingTheta)
        y = d * math.cos(self._gunHeadingTheta)
        
        # Calculate the height of the trajectory - normally y
        z0 = self._gunPower * math.cos(self._gunPitchTheta) * (t - 0.1) - (0.5 * GRAV_ACCEL * (t - 0.1)**2)
        z  = self._gunPower * math.cos(self._gunPitchTheta) * t - (0.5 * GRAV_ACCEL * t**2)
        
        # Calculate a new angle for the mortar
        dx = abs(d - d0)
        dy = z - z0       
        if (abs(dx) > 0):
            dTheta = math.atan(dy/dx)
            self._mortar.setP(dTheta)
            #print("(dtheta)=(%s)"%(dTheta * DEG_FACTOR))
        
        self._mortar.setPos(x,y,z)
        return t
    
    def explode(self):
        # This is stolen from the Texture-Swapping sample
        self.expPlane = loader.loadModel('assets/models/plane')  #load the object
        self.expPlane.reparentTo(self.baseNode)                  #reparent to render
        self.expPlane.setTransparency(1)                         #enable transparency
        
        self.expPlane.setScale(3)
        
        self.expPlane.setBin("fixed", 40)
        self.expPlane.setDepthTest(False)
        self.expPlane.setDepthWrite(False)
        
        #load the texture movie
        self.expTexs = self.loadTextureMovie(51, 'assets/textures/explosion/explosion',
                                             'png', padding = 4)
    
        #create the animation task
        self.expTaskCounter = 0
        self.expTask = taskMgr.add(self.textureMovie, "explosionTask")
        self.expTask.fps = 30                                 #set framerate
        self.expTask.obj = self.expPlane                      #set object
        self.expTask.textures = self.expTexs                  #set texture list
    
        #This create the "billboard" effect that will rotate the object soremove that it
        #is always rendered as facing the eye (camera)
        self.expPlane.node().setEffect(BillboardEffect.makePointEye())
    
    def doDamage(self, dist):
        damageFactor = 20
        self._damage += round(dist * damageFactor)
        
        if (self._damage > self._damageLimit):
            self.baseNode.removeNode()
        
        self.showInfo()
    
    def _checkHit(self):
        relativeHitPosition = self._mortar.getPos()
        worldPos = render.getRelativePoint(self.baseNode, relativeHitPosition)
        print("Check hit %s"%(self._mortar.getPos()))
        print("in the world %s"%(worldPos))
        self.game.checkHit(worldPos)
    
    #This function is run every frame by our tasks to animate the textures
    def textureMovie(self, task):
        currentFrame = int(task.time * task.fps)
        
        task.obj.setTexture(task.textures[currentFrame % len(task.textures)], 1)
        self.expTaskCounter += 1
        
        if (self.expTaskCounter < 400):
            return Task.cont
        else:
            self.expPlane.removeNode()
            return Task.done
    
    def loadTextureMovie(self, frames, name, suffix, padding = 1):
        return [loader.loadTexture((name+"%0"+str(padding)+"d."+suffix) % i) 
            for i in range(frames)]
        
class BattleShip(RepShip):
    _power = 20
    
    def __init__(self, pos=None,  hpr=None,  tag="", model='', parent=render):
        RepShip.__init__(self, pos, hpr, tag, model, parent)
        
        # NOTICE: the position is applied to baseNode so do not apply
        # positioning here
        self.model = loader.loadModel("assets/models/ship_01")
        self.model.setHpr(self.hpr)
        self.model.setTag('SelectorTag', self.tag)
        if self.aaLevel > 0:
            self.model.setAntialias(AntialiasAttrib.MMultisample, self.aaLevel)
        self.model.reparentTo(self.baseNode)
        
        self._movecursor = MoveCursor(self.baseNode, self, foot=1)
        
        #TESTING
        self.model.setColor(0.0, 0.3, 0.3)
    
        