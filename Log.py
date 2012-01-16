
# Python imports
import traceback
import inspect

# Game
import Event

# Ensure DEBUG is set
try:
	DEBUG
except NameError:
	DEBUG=4

class LogConsole(object):
	'''A class that listens for events and prints them out
	to the console'''
	
	def __init__(self, *args):
		self.log("Creating log console  [%s]"%(DEBUG))
	
	def start(self):
		''' The logger needs the Dispatcher but is usually created before the
			Dispatcher so we need to break the register part of creation out.'''
		self.log("Starting log console")
		Event.Dispatcher().register(self, 'E_All', self.printEvents)
		
	def printEvents(self, event):
		print("==DEBUG: Event Log============================================")
		print(str(event))
	
	def log(self, msg, type="N"):
		''' Depreciated, use one of debug(), notice(), warn(), error()'''
		if   type == "D": msgStart = "DEBUG: "
		elif type == "E":
			msgStart = "ERROR: "
			#traceback.print_tb()
			traceback.print_last()
		elif type == "N": msgStart = "NOTICE: "
		print("%s%s"%(msgStart, msg))
		
	def debug(self, msg, e=''):
		if (DEBUG >= 4):
			msgStart = "DEBUG:"
			#traceback.print_stack()
			print("%s %s"%(msgStart, msg))
			if (e != ''):
				print("  %s"%e)
	
	def notice(self, msg, e=''):
		if (DEBUG >= 3):
			msgStart = "NOTICE: "
			if (DEBUG == 4):
				#traceback.print_stack()
				pass
			print("%s%s"%(msgStart, msg))
			if (e != '' and DEBUG == 4):
				print("  %s"%e)
	
	def warn(self, msg, e=''):
		if (DEBUG >= 2):
			msgStart = "NOTICE: "
			if (DEBUG == 4):
				#traceback.print_stack()
				pass
			print("%s%s"%(msgStart, msg))
			if (e != '' and DEBUG == 4):
				print("  %s"%e)
	
	def error(self, msg, e=''):
		if (DEBUG >= 1):
			msgStart = "NOTICE: "
			if (DEBUG == 4):
				#traceback.print_stack()
				pass
			print("%s%s"%(msgStart, msg))
			if (e != '' and DEBUG == 4):
				print("  %s"%e)

    
#def printFBProps():
#	print("FRAMEBUFF PROPS--------------------------------")
#	print("accumbits " + str(fbProps.getAccumBits()))
#	print("multisamples " + str(fbProps.getMultisamples()))
#	print("alphabits " + str(fbProps.getMultisamples()))
#	print("accumbits " + str(fbProps.getAccumBits()))
#	print("colorbits " + str(fbProps.getColorBits()))
#	print("depthbits " + str(fbProps.getDepthBits()))
#	print("indexedcolor " + str(fbProps.getIndexedColor()))
#	print("rgbcolor " + str(fbProps.getRgbColor()))
#	print("stencilbits " + str(fbProps.getStencilBits()))
