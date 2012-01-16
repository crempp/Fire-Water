''' Controller.py
	
	Map keyboard / mouse controls to game objects

	Author:			Chad Rempp
	Date:			2009/05/07
	License:		GNU LGPL v3 
	Todo:			Add support for keymap options
'''

# Panda imports
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import CollisionHandlerQueue
from pandac.PandaModules import CollisionNode
from pandac.PandaModules import CollisionRay
from pandac.PandaModules import CollisionTraverser
from pandac.PandaModules import GeomNode

# Game imports
import Event

class KeyboardController(DirectObject):
	'''This class registers keyboard events with Panda3D and broadcasts events'''
	def __init__(self):
		
		# Register events
		self.accept("escape", Event.Dispatcher().broadcast, [Event.Event('E_Key_Exit', self)])
		self.accept("m",      Event.Dispatcher().broadcast, [Event.Event('E_Key_Move', self)])
		self.accept("arrow_up", Event.Dispatcher().broadcast, [Event.Event('E_Key_CameraUp', self)])
		self.accept("arrow_down", Event.Dispatcher().broadcast, [Event.Event('E_Key_CameraDown', self)])
		self.accept("arrow_left", Event.Dispatcher().broadcast, [Event.Event('E_Key_CameraLeft', self)])
		self.accept("arrow_right", Event.Dispatcher().broadcast, [Event.Event('E_Key_CameraRight', self)])
		self.accept("arrow_up-up", Event.Dispatcher().broadcast, [Event.Event('E_Key_CameraUp-up', self)])
		self.accept("arrow_down-up", Event.Dispatcher().broadcast, [Event.Event('E_Key_CameraDown-up', self)])
		self.accept("arrow_left-up", Event.Dispatcher().broadcast, [Event.Event('E_Key_CameraLeft-up', self)])
		self.accept("arrow_right-up", Event.Dispatcher().broadcast, [Event.Event('E_Key_CameraRight-up', self)])
		self.accept("page_up", Event.Dispatcher().broadcast, [Event.Event('E_Key_ZUp', self)])
		self.accept("page_down", Event.Dispatcher().broadcast, [Event.Event('E_Key_ZDown', self)])
		self.accept("page_up-up", Event.Dispatcher().broadcast, [Event.Event('E_Key_ZUp-up', self)])
		self.accept("page_down-up", Event.Dispatcher().broadcast, [Event.Event('E_Key_ZDown-up', self)])
		
class MouseController(DirectObject):
	'''This class registers mouse events with Panda3D and broadcasts events'''
	def __init__(self):
		# Register events
		self.accept("mouse1",     Event.Dispatcher().broadcast, [Event.Event('E_Mouse_1', self)])
		self.accept("mouse2",     Event.Dispatcher().broadcast, [Event.Event('E_Mouse_2', self)])
		self.accept("mouse3",     Event.Dispatcher().broadcast, [Event.Event('E_Mouse_3', self)])
		self.accept("mouse1-up",  Event.Dispatcher().broadcast, [Event.Event('E_Mouse_1_Up', self)])
		self.accept("mouse2-up",  Event.Dispatcher().broadcast, [Event.Event('E_Mouse_2_Up', self)])
		self.accept("mouse3-up",  Event.Dispatcher().broadcast, [Event.Event('E_Mouse_3_Up', self)])
		self.accept("wheel_up",   Event.Dispatcher().broadcast, [Event.Event('E_MouseWheel_Up', self)])
		self.accept("wheel_down", Event.Dispatcher().broadcast, [Event.Event('E_MouseWheel_Down', self)])

class Selector(object):
	'''A Selector listens for mouse clicks and then runs select. Select then
	   broadcasts the selected tag (if there is one)'''
	def __init__(self):
		''' Should the traverser be shared? '''
		
		LOG.debug("[Selector] Initializing")
		
		# The collision traverser does the checking of solids for collisions
		self.cTrav = CollisionTraverser()
		
		# The collision handler queue is a simple handler that records all
		# detected collisions during traversal
		self.cHandler = CollisionHandlerQueue()
		
		self.pickerNode = CollisionNode('mouseRay')
		self.pickerNP = camera.attachNewNode(self.pickerNode)
		self.pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
		self.pickerRay = CollisionRay()
		self.pickerNode.addSolid(self.pickerRay)
		self.cTrav.addCollider(self.pickerNP, self.cHandler)
		
		# Start listening to clicks
		self.resume()
		
	def select(self, event):
		LOG.debug("[Selector] Selecting ")
		if base.mouseWatcherNode.hasMouse():
			mpos = base.mouseWatcherNode.getMouse()
			self.pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())
			self.cTrav.traverse(render) # TODO - change this to a lower node
			if self.cHandler.getNumEntries() > 0:
				#LOG.debug("[Selector] Entries=%d"%self.cHandler.getNumEntries())
				self.cHandler.sortEntries()
				selectionNP = self.cHandler.getEntry(0).getIntoNodePath()
				selection = selectionNP.findNetTag('SelectorTag').getTag('SelectorTag')
				if selection is not '':
					LOG.debug("[Selector] Collision with %s"%selection)
					Event.Dispatcher().broadcast(Event.Event('E_EntitySelect', src=self, data=selection))
				else:
					LOG.debug("[Selector] No collision")
					#Event.Dispatcher().broadcast(Event.Event('E_EntityUnSelect', src=self, data=selection))
					
	def pause(self):
		Event.Dispatcher().unregister(self, 'E_Mouse_1')
		
	def resume(self):
		print("unpausing selector")
		Event.Dispatcher().register(self, 'E_Mouse_1', self.select)