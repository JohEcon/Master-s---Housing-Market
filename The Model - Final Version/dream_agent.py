# Peter Stephensen, DREAM 2019
# Version 0.1.  4-03-2019. First version
# Version 0.2. 10-03-2019. Fixing bug in get_random_agent()
# Version 0.3. 13-03-2019. Fixing bug in get_random_agent()
from Settings import *
import random
if Settings.random_seed != 0:
    random.seed(Settings.random_seed)
class Agent:
	"""Common base class for secret agents"""
	_nAgents = 0

	# Constructor 
	def __init__(self, parent=None):
		self._id = Agent._nAgents
		Agent._nAgents += 1
		self._first, self._next = None, None
		self._prev, self._last = None, None
		self._parent, self._a_itt = None, None
		self._count = 0
		self.removed, self.remove_when_empty = False, False
		self._random_agent=None
		
		if parent != None: parent.add_agent(self)

	def event_proc(self, id_event):
		for a in self:
			a.event_proc(id_event)
		
		if self.remove_when_empty and self._count==0:
			self.remove_this_agent()

	def add_agent(self, a):
		# Release old relations
		a.remove_this_agent()

		# Create new relations
		a._prev, a._next = self._last, None
		a._parent = self
    
		if self._first == None:
			self._first = a
		else:
			self._last._next = a

		self._last = a
		self._count += 1


	def remove_agent(self, a):
		removed = True

		if self._count==1:
			self._first, self._last = None, None
		else:
			if a._prev != None: a._prev._next = a._next
			if a._next != None: a._next._prev = a._prev
			
			if a == self._first: self._first = a._next
			if a == self._last: self._last = a._prev

		self._count -= 1


	def remove_this_agent(self):
		if self._parent != None:
			self._parent.remove_agent(self)

	def randomize_agents(self):
		if self._count>1:
			lst = []
			for a in self: lst.append(a)
			random.shuffle(lst)
			self._first, self._last = lst[0], lst[-1]
			lst[0]._prev, lst[0]._next = None, lst[1]
			lst[-1]._prev, lst[-1]._next = lst[-2], None
			if self._count>2:
				for i in range(1,self._count-1):
					lst[i]._prev, lst[i]._next = lst[i-1], lst[i+1]


	def get_random_agent(self, not_this_agent=None, n=1):
		# If no children
		if self._first == None:
			return None

		if self._random_agent == None:
			self._random_agent = self._first

		nn = n  #0.3
		if n > self._count:
			nn = self._count

		ls = []
		i = 0

		while (i < nn):
			if self._random_agent != not_this_agent or not_this_agent==None:
				ls.append(self._random_agent)
				i += 1
			if self._random_agent._next != None:
				self._random_agent = self._random_agent._next
			else:
				self._random_agent = self._first

		if nn == 1:
			return ls[0]
		else:
			return ls


	# Initialize iterator
	def __iter__(self):
		self._a_itt = self._first
		return self

	# Iterate iterator
	def __next__(self):
		if self._a_itt is not None:
			a = self._a_itt
			self._a_itt = self._a_itt._next
			return a
		else:	
			raise StopIteration

	def __eq__(self, other):
		return self._id==other

	def __ne__(self, other):
		return self._id!=other

	def __len__(self):
		if self._first==None:
			return 0
		else:
			return self._count

	def count(self):
		return self._count

	def get_number_of_agents(self):
		return self._count

	def number_of_agents(self):
		return self._count

	def get_id(self):
		return self._id

	def id(self):
		return self._id

	@staticmethod
	def get_total_number_of_agents():
		return Agent._nAgents


