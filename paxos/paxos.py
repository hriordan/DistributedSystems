
prop_num = 0 #global proposal number

class Proc: 

	def __init__(self):
	self.failed = False 	
	self.value  = 0   	#current value
	self.promises = []  #List of "promises"


class Message:

	def __init__(self, type, source, dest, value=0): #should src/dest be tuples to clarify set? 
		self.type = type
		self.source = source
		self.dest = dest
		self.value = value 


def init_procs(num):
	procs = []
	i = 0
	while i < num:
		procs.append(Proc())
		i++
	return procs


"""Searches for event in events list. returns empty tuple if not found"""
def extract_event(events, tick):
	for e in events: 
		if tick == e[0]:
			return e
	return ()


"""my parsing of input will result in failed and recovered being a list of tuples: (type, index). kool?
Type = prop or accept. index = ID in list"""
def simulate(nproposers, nacceptors, mtick, events):
	proposers = init_procs(nproposers) 
	accepters = init_procs(nacceptors)
	network = [] 

	for i in range(0,mtick):

		if len(network) == 0 and len(events) == 0: 
			return

		event = extract_event(events, i) 		#search events for event with tick i
		
		if len(event) != 0: 			
			del events[events.index(event)] 	#remove e from E
			tick, failed, recovered, proposer, value = event 
			
			for c,i in failed:
				if c == 'p':				 
					proposers[i].failed = True
				elif c == 'a':
					accepters[i].failed = True 

			for c in recovered:
				if c == 'p':				 
					proposers[i].failed = False
				elif c == 'a':
					accepters[i].failed = False

			if proposer != 0 and value != 0:   #Need to figure out a good analogue for "val/proposer != null/emptyset"
				 mes = Message("propose", 0, proposer, value)
		
				 deliver_message(proposers[proposer[1]], mes)

			else:
				mes = extract_message(network, proposers, acceptors)
				if mes:
					t,i = mes.dst 
					if t == 'p':	 	
						deliver_message(proposers[i], mes)
					else:
						deliver_message(accepters[i], mes)

		else: 
			mes = extract_message(network)
			if mes: 
				t,i = mes.dst 
					if t == 'p':	 	
						deliver_message(proposers[i], mes)
					else:
						deliver_message(accepters[i], mes)


def extract_message(network, proposers, accepters):
	dest, src = 0	

	for m in network:

		i = m.dest[1]
		if m.dest[0] == 'p':
			if proposers[i].failed == False:
				dest = 1
		else:
			if acceptors[i].failed == False:
				dest = 1

		i = m.src[1]
		if m.src[0] == 'p':
			if proposers[i].failed == False:
				src = 1
		else:
			if acceptors[i].failed == False:
				src = 1

		if dest and src:
			ind = network.index[m]
			mes = network.pop[ind]
			return mes

	return 0 	  #return 0 if no message found. okay?

