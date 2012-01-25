
# Python imports
import math

# Panda imports
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import Vec3
from pandac.PandaModules import Vec2
from pandac.PandaModules import Vec4
from pandac.PandaModules import Mat4
from pandac.PandaModules import Mat3

# Game imports
import Event
from Representations import Representation

RAD_FACTOR = (math.pi / 180)

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

        #LOG.debug("self.pos = %s, self.target = %s, self.camDist = %s" % (self.pos, self.target, self.camDist))        
        
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
        self.zoomFactor = 3
        
        
        # Build the camera rotation maticies
        self.leftrightRotationDegrees = 0.5
        self.updownRotationDegrees    = 2
        
        rSin = math.sin(self.leftrightRotationDegrees * RAD_FACTOR)
        rCos = math.cos(self.leftrightRotationDegrees * RAD_FACTOR)
        self.leftMatrix  = Mat3( rCos,  rSin,  0,
                                -rSin,  rCos,  0,
                                 0,     0,     1)
        self.rightMatrix = Mat3( rCos, -rSin,  0,
                                 rSin,  rCos,  0,
                                 0,     0,     1)
        rSin = math.sin(self.updownRotationDegrees * RAD_FACTOR)
        rCos = math.cos(self.updownRotationDegrees * RAD_FACTOR)
        self.upMatrix    = Mat3( rCos,  0,     -rSin,
                                 0,     1,     0,
                                 rSin,  0,     rCos)
        self.downMatrix  = Mat3( rCos,  0,     rSin,
                                 0,     1,     0,
                                -rSin,  0,     rCos,)
        #self.upMatrix    = Mat3( 1,     0,     0,
        #                         0,     rCos, -rSin,
        #                         0,     rSin,  rCos)
        #self.downMatrix  = Mat3( 1,     0,     0,
        #                         0,     rCos,  rSin,
        #                         0,    -rSin,  rCos)
        
    def startCamera(self):
        LOG.debug("Starting CameraManager")
        
        # Register with Dispatcher
        Event.Dispatcher().register(self, 'E_Mouse_3', self.startDrag)
        Event.Dispatcher().register(self, 'E_Mouse_3_Up', self.stopDrag)
        Event.Dispatcher().register(self, 'E_MouseWheel_Up', self.adjustCamDist)
        Event.Dispatcher().register(self, 'E_MouseWheel_Down', self.adjustCamDist)
        
        # Turn off default camera movement
        base.disableMouse()
        
        # Set camera properties
        base.camLens.setFov(self.fov)
        base.camera.setPos(self.pos)
        
        self.updateCamera()
        
        taskMgr.add(self.mousePositionTask,'mousePositionTask')
        
    def updateCamera(self):
        ''' Update the camera position and angle.
        
        
        '''
        base.camera.setPos(self.pos)
        #LOG.debug("%s"%(self.target))
        base.camera.lookAt( self.target.getX(), self.target.getY(), self.target.getZ() )
        
        
    def setTarget(self,x,y = None, z = None):
        #print (x.pos)
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
        
        deltaVec      = cameraVecNorm * self.zoomFactor
        
        if event.type == 'E_MouseWheel_Up':
            self.pos = self.pos + deltaVec
        elif event.type == 'E_MouseWheel_Down':
            self.pos = self.pos - deltaVec
            
        self.resetMousePos()
        self.updateCamera()
        
    def mousePositionTask(self,task):
        ''' Update the camera depending on certain click states and the mouse position '''
        
        if base.mouseWatcherNode.hasMouse():
            
            # Get current mouse position
            self.mpos = base.mouseWatcherNode.getMouse()
            
            if self.dragging:
                # If we are dragging spin the camera around the central point
                
                # The following will not be needed if I get the z-axis rotation
                # matrix to work
                cameraVec = self.target - self.pos
                distFact  = ( 1 / cameraVec.length() )
                
                # Get the distance the mouse has moved
                mouse_dx = (self.mx - self.mpos.getX())
                mouse_dy = (self.my - self.mpos.getY()) * self.panMouseFactor * distFact
                
                if (not mouse_dx == 0):
                    if (mouse_dx > 0):
                        newPos = self.leftMatrix.xformVec(self.pos)
                    else:
                        newPos = self.rightMatrix.xformVec(self.pos)
                    
                    self.pos.setX(newPos.getX())
                    self.pos.setY(newPos.getY())
                if (not mouse_dy == 0):
                    #if (mouse_dy > 0):
                    #    newPos = self.upMatrix.xformVec(self.pos)
                    #else:
                    #    newPos = self.downMatrix.xformVec(self.pos)
                    #LOG.debug("newPos = %s" % (newPos))
                    #self.pos.setZ(newPos.getZ())
                    self.pos.setZ(self.pos.getZ() + mouse_dy)
                
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
            
        return task.cont

    def resetMousePos(self):
        #LOG.debug("RESET")
        self.mx = self.mpos.getX()
        self.my = self.mpos.getY()
    
