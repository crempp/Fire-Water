''' Singleton.py
	
	Define the singleton object

	Author:			Chad Rempp
	Date:			2009/05/07
	License:		GNU LGPL v3 
	Todo:			
'''

class Singleton(type):
	''' Singleton Design Pattern (Recipe 412551)
	
		This ensures that only one instance of the class is ever created.
		It is possible to access Singletons by just calling the class name, eg:
		Singleton().function()
	'''
	def __init__(self, *args):
		type.__init__(self, *args)
		self._instances = {}

	def __call__(self, *args):
		if not args in self._instances:
			self._instances[args] = type.__call__(self, *args)
		return self._instances[args]