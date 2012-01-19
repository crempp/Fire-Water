
# Python imports
import math

# Panda imports
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import Vec3
from pandac.PandaModules import Vec2

# Game imports
import Event
from Representations import Representation

class CameraManager(DirectObject):
    ''' A class that controls the camera
        
        Internally positions must be represented by Vec3
    '''
    def __init__(self, fov=60.0, pos=(-10,-100,25), lookAt=(0,0,0)):
        
        # Camera field of view        
        self.fov     = fov
        
        # Camera position
        self.pos     = Vec3(pos)
        
        # Point the camera looks at
        self.lookAt  = Vec3(lookAt)
        
        # Camera target. This is what the camera should be looking at
        self.target  = Vec3(lookAt)
        
        #
        camVec = (self.target - self.pos)
        self.camDist = camVec.length()

        LOG.debug("self.pos = %s, self.target = %s, self.camDist = %s" % (self.pos, self.target, self.camDist))        
        
        # Camera state variables
        self.movingUp    = False
        self.movingDown  = False
        self.movingLeft  = False
        self.movingRight = False
        self.dragging    = False

        # The gutter is the area around the border of the screen where
        # the mouse cursor entering this area triggers the panning action
        self.leftgutter   = -0.8
        self.rightgutter  =  0.8
        self.bottomgutter = -0.8
        self.topgutter    =  0.8
        
        # Mouse position from previous event. Used to calculate distance the
        # mouse has moved.
        self.mx = 0
        self.my = 0
        self.mpos = Vec2(0,0)
        
        # Options
        self.gutterdrive = False
        # Factor used to convert mouse movement into world movement
        self.gutterdriveMouseFactor = 100
        self.panMouseFactor = 2000
        
    def startCamera(self):
        LOG.debug("Starting CameraManager")
        
        # Register with Dispatcher
        Event.Dispatcher().register(self, 'E_Mouse_3', self.startDrag)
        Event.Dispatcher().register(self, 'E_Mouse_3_Up', self.stopDrag)
        Event.Dispatcher().register(self, 'E_MouseWheel_Up', self.adjustCamDist)
        Event.Dispatcher().register(self, 'E_MouseWheel_Down', self.adjustCamDist)
        #Event.Dispatcher().register(self, 'E_Key_CameraUp', self.keyMove)
        #Event.Dispatcher().register(self, 'E_Key_CameraUp-up', self.keyMove)
        #Event.Dispatcher().register(self, 'E_Key_CameraDown', self.keyMove)
        #Event.Dispatcher().register(self, 'E_Key_CameraDown-up', self.keyMove)
        #Event.Dispatcher().register(self, 'E_Key_CameraLeft', self.keyMove)
        #Event.Dispatcher().register(self, 'E_Key_CameraLeft-up', self.keyMove)
        #Event.Dispatcher().register(self, 'E_Key_CameraRight', self.keyMove)
        #Event.Dispatcher().register(self, 'E_Key_CameraRight-up', self.keyMove)
        
        # Turn off default camera movement
        base.disableMouse()
        
        # Set camera properties
        base.camLens.setFov(self.fov)
        base.camera.setPos(self.pos)
        
        # The lookAt camera method doesn't work right at the moment.
        # This should be moved into a seperate method of Camera Manager anyway
        # so we can set this to the players start pos.
        #base.camera.lookAt(self.lookAt)
        
        self.updateCamera()
        
        taskMgr.add(self.mousePositionTask,'mousePositionTask')
        
    def updateCamera(self):
        ''' Update the camera position and angle.
        
        
        '''
        
        base.camera.setPos(self.pos)
        base.camera.lookAt( self.target.getX(), self.target.getY(), self.target.getZ() )
        #LOG.debug("HPR = %s, POS= %s" % (base.camera.getHpr(), base.camera.getPos()))
        
        
    def setTarget(self,x,y = None, z = None):
        print (x.pos)
        if (issubclass(x.__class__, Representation)):
            nx = x.pos[0]
            ny = x.pos[1]
            nz = x.pos[2]
        else:
            nx = x
            ny = y
            nz = z
        
        self.target.setX(nx)
        self.target.setY(ny)
        self.target.setZ(nz)
        
        self.updateCamera()
        
    def startDrag(self, event):
        self.dragging=True
        
    def stopDrag(self, event):
        self.dragging=False
        
    def adjustCamDist(self, event):
        # Vector from camera to target
        cameraVec     = self.target - self.pos
        # Normalized vector
        cameraVecNorm = cameraVec
        cameraVecNorm.normalize()
        
        deltaVec      = cameraVecNorm
        LOG.debug("self.pos = %s, deltaVec = %s" % (self.pos, deltaVec))
        
        if event.type == 'E_MouseWheel_Up':
            self.pos = self.pos + deltaVec
        elif event.type == 'E_MouseWheel_Down':
            self.pos = self.pos - deltaVec
            
        #LOG.debug("self.camDist = %s" % (self.camDist))
        #self.camDist = self.camDist * aspect
        self.resetMousePos()
        self.updateCamera()
        
    def mousePositionTask(self,task):
        ''' Update the camera depending on certain click states and the mouse position '''
        
        if base.mouseWatcherNode.hasMouse():
            
            # Get current mouse position
            self.mpos = base.mouseWatcherNode.getMouse()
            
            if self.dragging:
                # If we are dragging spin the camera around the central point
                # Vector from camera to target
                cameraVec = self.target - self.pos
                #LOG.debug("cameraVec = %s" % (cameraVec))
                distFact  = ( 1 / cameraVec.length() )
                #LOG.debug("cameraVec.length() = %s" % (cameraVec.length()))
                #LOG.debug("distFact = %s" % (distFact))
                
                #LOG.debug("(mx, my) = (%s, %s)" % (self.mx, self.my))
                #LOG.debug("mpos = (%s, %s)" % (self.mpos.getX(), self.mpos.getY()))
                #LOG.debug("(mdx, mdy) = (%s, %s)" % ((self.mx - self.mpos.getX()), (self.my - self.mpos.getY())))
                
                dx = (self.mx - self.mpos.getX()) * self.panMouseFactor * distFact
                dy = 0
                dz = (self.my - self.mpos.getY()) * self.panMouseFactor * distFact
                
                #LOG.debug("D = (%s, %s, %s)" % (dx, dy, dz))
                
                self.pos.setX(self.pos.getX() + dx)
                self.pos.setY(self.pos.getY() + dy)
                self.pos.setZ(self.pos.getZ() + dz)
                
                self.updateCamera()
            
            elif self.gutterdrive:
                # Otherwise handle panning
                moveY=False
                moveX=False

                panFactor = 2                
                
                # The mouse is within the bottom gutter so pan south
                if self.my > self.topgutter:
                    angleradiansX = base.camera.getH() * (math.pi / 180.0)
                    aspect        = ( 1 - self.my - 0.2 ) * panFactor
                    moveY=True
                    
                # The mouse is within the bottom gutter so pan south
                if self.movingUp:
                    angleradiansX = base.camera.getH() * (math.pi / 180.0)
                    aspect=(1 - (0.95) - 0.2) * panFactor
                    moveY=True
                
                if self.my < self.bottomgutter:
                    angleradiansX = base.camera.getH() * (math.pi / 180.0) + math.pi
                    aspect=(1 + self.my - 0.2) * panFactor
                    moveY=True
                    
                if self.movingDown:
                    angleradiansX = base.camera.getH() * (math.pi / 180.0) + math.pi
                    aspect=(1 + (-0.95) - 0.2) * panFactor
                    moveY=True
                    
                if self.mx > self.rightgutter:
                    angleradiansX2 = base.camera.getH() * (math.pi / 180.0)+math.pi * 0.5
                    aspect2=(1 - self.mx - 0.2) * panFactor
                    moveX=True
                    
                if self.movingRight:
                    angleradiansX2 = base.camera.getH() * (math.pi / 180.0)+math.pi * 0.5
                    aspect2=(1 - (0.95) - 0.2) * panFactor
                    moveX=True
                    
                if self.mx < self.leftgutter:
                    angleradiansX2 = base.camera.getH() * (math.pi / 180.0)-math.pi * 0.5
                    aspect2=(1 + self.mx - 0.2) * panFactor
                    moveX=True
                    
                if self.movingLeft:
                    angleradiansX2 = base.camera.getH() * (math.pi / 180.0) - math.pi * 0.5
                    aspect2=(1 + (-0.95) - 0.2) * panFactor
                    moveX=True
                
                if moveY:   
                    self.target.setX(self.target.getX() + math.sin(angleradiansX) * aspect)
                    self.target.setY(self.target.getY() - math.cos(angleradiansX) * aspect)
                    self.resetMousePos()                    
                    self.updateCamera()
                if moveX:
                    self.target.setX( self.target.getX() - math.sin(angleradiansX2) * aspect2 )
                    self.target.setY( self.target.getY() + math.cos(angleradiansX2) * aspect2 )
                    self.resetMousePos()
                    self.updateCamera()
            
            self.mx = self.mpos.getX()
            self.my = self.mpos.getY()
            
            #LOG.debug("(mx, my) = (%s, %s)" % (self.mx, self.my))
        return task.cont

    def resetMousePos(self):
        #LOG.debug("RESET")
        self.mx = self.mpos.getX()
        self.my = self.mpos.getY()
    
    #def keyMove(self, event):
    #    if event.type == 'E_Key_CameraUp':
    #        self.movingUp = True
    #    elif event.type =='E_Key_CameraUp-up':
    #        self.movingUp = False
    #    elif event.type =='E_Key_CameraDown':
    #        self.movingDown = True
    #    elif event.type =='E_Key_CameraDown-up':
    #        self.movingDown = False
    #    elif event.type =='E_Key_CameraLeft':
    #        self.movingLeft = True
    #    elif event.type =='E_Key_CameraLeft-up':
    #        self.movingLeft = False
    #    elif event.type =='E_Key_CameraRight':
    #        self.movingRight = True
    #    elif event.type =='E_Key_CameraRight-up':
    #        self.movingRight = False
