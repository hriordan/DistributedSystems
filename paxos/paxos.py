import copy 

prop_num = 1 #global proposal number
network = [] #global network variable 


class Proc: 

	def __init__(self, myid, nacceptors):
		self.myid = myid 
		self.failed = False 	
		self.consensus  = ()   	#current proposal accepted
		self.accepted = ()  
		self.promises = 0    	#promised id number 
		self.proposals = []		#or dictionary with key:value --> propid: prop_object ?
		self.nacceptors = nacceptors


class Message:

	def __init__(self, mtype, source, dest, attributes): #attributes is a dictionary of stuff 
		self.type = mtype
		self.source = source
		self.dest = dest
		self.attributes =  attributes

	def print_mes(self,tick):
		if self.type == "prepare":
				print "%d: P%d -> A%d %s n=%d" % (tick, self.source[1]+1, self.dest[1]+1, self.type, self.attributes["propid"])
		
		elif self.type == "promise":
			if self.attributes["Prior"] == ():
				prior = "None"
			else:
				prior = "n=%d, v=%d" % self.attributes["Prior"][0], self.attributes["Prior"][1]		
			print "%d: A%d -> P%d %s n=%d (Prior: %s)" % (tick, self.source[1]+1, self.dest[1]+1, self.type, self.attributes["promid"], prior)
	
		elif self.type == "accept":
			print "%d: P%d -> A%d %s n=%d v=%d" % (tick, self.source[1]+1, self.dest[1]+1, self.type, self.attributes["accepting"][0], int(self.attributes["accepting"][1]))

		elif self.type == "accepted":
			print "%d: A%d -> P%d %s n=%d v=%d" % (tick, self.source[1]+1, self.dest[1]+1, self.type, self.attributes["accepted"][0], int(self.attributes["accepted"][1]))

		elif self.type == "rejected":
			print "%d: A%d -> P%d %s n=%d" % (tick, self.source[1]+1, self.dest[1]+1, self.type, self.attributes["propid"])

		else:
			print "%s is not a message type" % self.type




class Proposal: 

	def __init__(self, pid, pvalue):
		self.promised = False	#is there a majority promising?
		self.votecount = 0		#RENAME TO PROMCOUNT  
		self.approved = False	#is there a majority accepting? 
		self.id = pid
		self.value = pvalue 
		self.myhighestval = (pid, pvalue)
		self.rejectcount = 0
		self.acceptcount = 0 





def init_procs(num): #number of objects, proposer boolean
	procs = []
	i = 0
	while (i < num): 
		procs.append(Proc(i, num)) #i is the ID# of proc 
		i = i + 1
	return procs


"""Searches for event in events list. returns empty tuple if not found"""
def extract_events(events, tick):
	evs = []
	for e in events: 
		if tick == e[0]:
			evs.append(e)
	return evs 


"""my parsing of input will result in failed and recovered being a list of tuples: (type, index). kool?
Type = prop or accept. index = ID in list"""
def simulate(nproposers, nacceptors, mtick, events):
	proposers = init_procs(nproposers) 
	accepters = init_procs(nacceptors)

	for prop in proposers:
		prop.nacceptors = nacceptors

	print "SIMULATING"
	for ti in range(0, mtick):

		if len(network) == 0 and len(events) == 0: 
			for prop in proposers:
				if prop.consensus != ():
					print "P%d has reached consensus (Proposed %d, accepted %d)" % (prop.myid, int(prop.proposals[0].value), int(prop.consensus[1]))
				else:
					print "P%d did not reach consensus" % prop.myid
			return

		events = extract_events(events, ti) 		#search events for event with tick i
		
		if events != []:
			for event in events: 			
				del events[events.index(event)] 	#remove e from E
				tick, failed, recovered, proposer, value = event 
				

				if failed != ():
					c,i = failed 
					if c == 'p':				 
						proposers[i-1].failed = True
						print str(ti) + ": ** P" + str(i+1) + " FAILS **"

					elif c == 'a':
						accepters[i-1].failed = True 
						print str(ti) + ": ** A" + str(i+1) + " FAILS **"
						

				if recovered != ():
					c,i = recovered
					if c == 'p':				 
						proposers[i-1].failed = False
						print str(ti) + ": ** P" + str(i+1) + " RECOVERS **"
						
					elif c == 'a':
						accepters[i-1].failed = False
						print str(ti) + ": ** A" + str(i+1) + " RECOVERS **"


				if proposer != () and value != ():   #Need to figure out a good analogue for "val/proposer != null/emptyset"
					mes = Message("propose", 0, proposer, {"value": value, "numaccept": nacceptors})  	#woo dictionary literal
					deliver_message(proposers[proposer[1]-1], mes)	#proposer is tuple. 

					print str(ti) + ":    -> P" + str(proposer[1]) + " PROPOSE V=" + str(value)
					
		else:
			mes = extract_message(network, proposers, accepters)
			if mes:
				t,i = mes.dest 
				s,b = mes.source 
				if t == 'p':	 	

					deliver_message(proposers[i-1], mes)
					mes.print_mes(ti)
					
				else:
					deliver_message(accepters[i-1], mes)
					mes.print_mes(ti)
	for prop in proposers:
		if prop.consensus != ():
			print prop.consensus
		else:
			print "no consensus" 




def deliver_message(dest, mes):
	"""Proposer"""
	if mes.type == "propose":
		global prop_num
		propid = prop_num
		prop_num += 1
		
		nacceptors = mes.attributes["numaccept"]
		value = mes.attributes["value"]

		proposal = Proposal(propid, value)
		proposal.myhighestval = (propid,value)  
		dest.proposals.append(proposal)

		for acceptor in range(0, nacceptors):
			#create new message and queue it
			mes = Message("prepare", ('p',dest.myid), ('a',acceptor), {"propid": propid})
			queue_message(mes, network)		

		return 

			#"""Prepare"""	
	elif mes.type == "prepare":  
		propid = mes.attributes["propid"]

		if propid > dest.promises: 	#promise to not participate in higher values 
			#dest.proposals.append(Proposal(propid, value)) #remember proposals I got? Needed for Accepter? 
			dest.promises = propid
			
			mes = Message("promise", ('a', mes.dest[1]), ('p', mes.source[1]), {"promid": propid, "Prior": dest.accepted})
			queue_message(mes, network)
		else: 					   	#earlier proposal id, so reject
			mes = Message("rejected", ('a', mes.dest[1]), ('p', mes.source[1]), {"propid": propid})
			queue_message(mes, network)

		return

	#"""promise"""
	elif mes.type == "promise":   					#proposer receives a promise
		propid = mes.attributes["promid"]
		proposal = _find_proposal(dest.proposals, propid)  	#pull the relevant proposal from list/dict

		if proposal.promised:  	 
			 #do nothing as who gives a fuck its already promised and its impossible for another value to be accepted
			 return 
		else: 
			if mes.attributes["Prior"] == ():
				pass  
			elif mes.attributes["Prior"][1] > proposal.myhighestval[1]:  #if reported value is higher than current one
				proposal.myhighestval = mes.attributes["Prior"]

			proposal.votecount += 1 		
	
			if proposal.votecount > dest.nacceptors/2.0: 
				proposal.promised = True
				for i in range(0,dest.nacceptors):
					mes = Message("accept", ('p', dest.myid), ('a', i), {"accepting": (proposal.id, proposal.myhighestval[1])})
					queue_message(mes, network)
			return 

	#"""accept"""
	elif mes.type == "accept": 
		recv_prop = mes.attributes["accepting"][0]
		if recv_prop < dest.promises: #reject it as its a lower prop number than we already promised 
			mes = Message("rejected", ('a', mes.dest[1]), ('p', mes.source[1]), {"propid": recv_prop})
			queue_message(mes, network)
			return #lower proposal number
		else: #accepted!
			dest.accepted = mes.attributes["accepting"]	#we accept this one as god. 
			mes = Message("accepted", ('a', mes.dest[1]), ('p', mes.source[1]), {"accepted": mes.attributes["accepting"]})
			queue_message(mes, network)
			return 

	#"""Rejected"""
	elif mes.type == "rejected":
		propid = mes.attributes["propid"]
		proposal = _find_proposal(dest.proposals, propid)
		
		if proposal.rejectcount > dest.nacceptors/2.0: 	#already rejected
			return
		else: 
			proposal.rejectcount += 1
			if proposal.rejectcount > dest.nacceptors/2.0: # act like you are prposoing a new message 
				mes = Message("propose", (), ('p',dest.myid), {"value": proposal.value, "numaccept": dest.nacceptors})  	#woo dictionary literal
				deliver_message(proposers[proposer[1]], mes) #recursion...yay? 
				return 

	#"""accepted"""
	elif mes.type == "accepted":
		propid = mes.attributes["accepted"][0]
		proposal = _find_proposal(dest.proposals, propid) #the "value" is guaranteed to be associated with the highest value
 
		if proposal.acceptcount > dest.nacceptors/2.0: #already accepted
			return
		else:
			proposal.acceptcount += 1
			if proposal.acceptcount > dest.nacceptors/2.0: #win!
				dest.consensus = proposal.myhighestval
				return

"""STILL NEED TO DOUBLE CHECK ALL CLASS VARIABLES/everything else""" 

def _find_proposal(proplist, propid):
	for p in proplist:
		if p.id == propid:
			return p #yes? Or can i just return p?  
	print "no proposal with id " + str(propid) + " found"
	exit(1) 



def extract_message(network, proposers, accepters):
	dest = 0	
	src = 0

	for index,m in enumerate(network):

		i = m.dest[1]
		if m.dest[0] == 'p':
			if proposers[i].failed == False:
				dest = 1
		else:
			if accepters[i].failed == False:
				dest = 1

		i = m.source[1]
		if m.source[0] == 'p':
			if proposers[i].failed == False:
				src = 1
		else:
			if accepters[i].failed == False:
				src = 1

		if dest and src:
			ind = index
			mes = network[ind]
			del network[ind]
			return mes

	return 0 	  #return 0 if no message found. okay


def queue_message(mes,net):
	net.append(mes)


"""Here lies IO """
def read_info():
	stuff = raw_input()
	while len(stuff.strip()) == 0 or stuff[0] == "#":
		print "stuff" + stuff
		stuff = raw_input()

	
	initinfo = stuff
	initinfo = initinfo.split(" ")
	#print initinfo
	np = int(initinfo[0])
	na = int(initinfo[1])
	tmax = int(initinfo[2])

	events = []

	inputs = raw_input()
	while inputs.split(" ")[1] != "END":
		if inputs[0] == "#":	#ignore comments 
			inputs = raw_input()
			continue

		if len(inputs.strip()) == 0: #ignore white lines
			inputs = raw_input()
			continue 

		inputs = inputs.split(" ")
		print inputs  
		tick = inputs[0] 
		fail = ()
		recover = ()
		proposer = ()
		value = ()

		if inputs[1] == "PROPOSE":
			proposer = ('p',int(inputs[2]))
			value = inputs[3]

		elif inputs[1] == "FAIL":
			if inputs[2] == "PROPOSER":
				fail = ('p',int(inputs[3]))
			else:
				fail = ('a', int(inputs[3]))

		elif inputs[1] == "RECOVER":
			if inputs[2] == "PROPOSER":
				recover = ('p',int(inputs[3]))
			else:
				recover = ('a', int(inputs[3]))

		events.append( (int(tick), fail, recover, proposer, value) )

		inputs = raw_input()

	print np
	print na
	print tmax
	print events
	simulate(np, na, tmax, events)


read_info()
