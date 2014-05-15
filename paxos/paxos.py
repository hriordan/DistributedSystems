
prop_num = 1 #global proposal number
network = [] #global network variable 


class Proc: 

	def __init__(self, myid, nacceptors):
		self.myid = myid 
		self.failed = False 	
		self.consensus  = ()   	#current proposal accepted  
		self.promises = 0    	#promised id number 
		self.proposals = []		#or dictionary with key:value --> propid: prop_object ?
		self.nacceptors = nacceptors
		self.myhighestval = 0 #NEED TO DELETE  

class Message:

	def __init__(self, mtype, source, dest, attributes): #attributes is a dictionary of stuff 
		self.type = mtype
		self.source = source
		self.dest = dest
		self.value = value 
		self.attributes =  attributes


class Proposal: 

	def __init__(self, pid, pvalue):
		self.promised = False	#is there a majority promising?
		self.votecount = 0		#RENAME TO PROMCOUNT  
		self.approved = False	#is there a majority accepting? 
		self.id = pid
		self.value = pvalue 
		self.myhighestval = ()
		self.rejectcount = 0
		self.acceptcount = 0 



def init_procs(num, proposer=0): #number of objects, proposer boolean
	procs = []
	i = 0
	while i < num:
		if proposer: 
			procs.append(Proc(i, num)) #i is the ID# of proc 
		i += 1
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
	proposers = init_procs(nproposers, 1) 
	accepters = init_procs(nacceptors)

	for i in range(0, mtick):

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
				 mes = Message("propose", 0, proposer, {"value": value, "numaccept": nacceptors})  	#woo dictionary literal
		
				 deliver_message(proposers[proposer[1]], mes)	#proposer is tuple. 

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



def deliver_message(dest, mes):
	"""Proposer"""
	if mes.type == "propose":
		propid = prop_num
		prob_num += 1
		
		nacceptors = mes.attributes["numaccept"]
		value = mes.attributes["value"]

		proposal = Proposal(propid, value)
		proposal.myhighestval = (propid,value)  
		dest.proposals.append(Proposal(proposal))

		for acceptor in range(0, nacceptors):
			#create new message and queue it
			mes = Message("prepare", ('p',dest.myid), ('a',acceptor), {"propid": propid})
			queue_message(mes, network)		

		return 

			#"""Prepare"""	
	elif mes.type == "prepare":  
		propid = mes.attributes["propid"]

		if propid > dest.promises: 	#promise to not participate in higher values 
			dest.proposals.append(Proposal(propid, value)) #remember proposals I got? Needs solution.
			dest.promises = propid
			
			mes = Message("promise", ('a', mes.dest), ('p', mes.source), {"promid": propid, "Prior": dest.accepted})
			queue_message(mes, network)
		else: 					   	#earlier proposal id, so reject
			mes = Message("rejected", ('a', mes.dest), ('p', mes.source), {"propid": dest.promises})
			queue_message(mes, network)

		return

	#"""promise"""
	elif mes.type == "promise":   					#proposer receives a promise
		propid = mes.attributes["promid"]
		proposal = _find_proposal(self.proposals, propid)  	#pull the relevant proposal from list/dict

		if proposal.promised:  	 
			 #do nothing as who gives a fuck its already promised and its impossible for another value to be accepted
			 return 
		else: 
			if mes.attributes["Prior"][1] > proposal.myhighestval[1]:  #if reported value is higher than current one
				proposal.myhighestval = mes.attributes["Prior"]

			proposal.votecount += 1 

			if proposal.votecount > dest.nacceptors/2.0: 
				proposal.promised = True
				for i in range(0,nacceptors):
					mes = Message("accept",('p', mes.dest), ('a', i), {"accepting": proposal.myhighestval})
					queue_message(mes, network)

			return 
	#"""accept"""
	elif mes.type == "accept": 

		recv_prop = mes.attributes["accepting"][0]
		if recv_prop < dest.promises: #reject it as its a lower prop number than we already promised 
			mes = Message("rejected", ('a', mes.dest), ('p', mes.source), {"propid": recv_prop})
			queue_message(mes, network)
			return #lower proposal number
		else: #accepted!
			mes = Message("accepted", ('a', mes.dest), ('p', mes.source), {"accepted": mes.attributes["accepting"]})
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
		propid = mes.attributes["accepted"]
		proposal = _find_proposal(dest.proposals, propid) #the "value" is guaranteed to be associated with the highest value
 
		if proposal.acceptcount > dest.nacceptors/2.0: #already accepted
			return
		else:
			proposal.acceptcount += 1
			if proposal.acceptcount > dest.nacceptors/2.0: #already accepted
				dest.consensus = proposal.myhighestval
				return

"""STILL NEED TO DOUBLE CHECK ALL CLASS VARIABLES/everything else""" 


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

	return 0 	  #return 0 if no message found. okay


def queue_message(mes,net):
	net.append(mes)


"""Here lies IO """
def read_in():
	pass

print "hji"

