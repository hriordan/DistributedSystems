"""Henry Riordan, 2014. Simluation of the Byzantine General's Algorithm"""

import copy

verbose = 0 #for debugging purposes

class orders:
    attack = 1
    retreat = 2
    tie = 3
    
def ordertostring(order):
    if order == orders.attack:
        return "A"
    elif order == orders.retreat:
        return "R"
    elif order == orders.tie:
        return "-"
    else:
        return "?"

class General:
    'general node-processor class' 
    nodeCount = 0
    
    def __init__(self, id, loyalty):
        self.id = id

        if loyalty == 'L':
            self.loyal = True
        else:
            self.loyal = False

        General.nodeCount += 1
        
        self.order = orders.retreat 
        self.original = 4 #NULL value 
        self.ordict = {}  #global orders dictionary consisting of a prefix keys and order values
                          #e.g. '013': 'attack' ==>3 said 1 said 0 ordered attack 

    def __eq__(self, other):
        if self.id == other.id:
            return True
        else:
            return False


    def tell_orders(self, generals, prefix):
        key = ''.join([prefix, str(self.id)])          
        self.ordict[key] = self.ordict[prefix] #"tell yourself what you are talking about" --redundant, but helpful in passing orders btw layers

        if self.loyal == True: 
            for gen in generals:
                gen.ordict[key] = self.ordict[key]
                if self.id == 0: 
                    gen.original = self.ordict[key]
                if verbose:
                    print "I, " + str(self.id) + " told general " + str(gen.id) + " to " + str(self.ordict[key]) + " for prefix" + prefix

        else: #Traitor! 
            for gen in generals:

                if gen.id % 2 == 0: 
                
                    if self.ordict[key] == orders.retreat:
                        gen.ordict[key] = orders.attack
                        if self.id == 0: 
                            gen.original = orders.attack #janky solution for saving original order. update somehow if possible
                    else:
                        gen.ordict[key] = orders.retreat
                        if self.id == 0:
                            gen.original = orders.retreat
                
                else:
                    gen.ordict[key] = self.ordict[key] 
                    if self.id == 0:
                        gen.original = self.ordict[key]



    def printgen(self, prefix, others):
        orderlist = ""
        orderlist += ordertostring(self.original) + " " # original order from commander 

        for gen in others: 
            if self == gen: 
                orderlist += " " 
            else:
                key = prefix + str(gen.id)
                if self.ordict[key] == orders.attack:
                    orderlist += "A"
                elif self.ordict[key] == orders.retreat:
                    orderlist += "R"
                elif self.ordict[key] == orders.tie:
                    orderlist += "-"
                else:
                    orderlist += "%" #error 

        if self.order == orders.attack:
            orderlist += "  ATTACK"
        elif self.order == orders.retreat:
            orderlist += "  RETREAT"
        elif self.order == orders.tie:
            orderlist += "  TIE"
        else:
            print "How did you get an order other than the default 3? " + str(gen.order)
            exit(1)

        print orderlist



def readorders(): #reads in orders and returns a list of them
    orderset = []
    
    inputs = raw_input()
    while inputs.split(" ")[1] != "END":
        orderset.append(inputs.split(" "))
        inputs = raw_input()

    return orderset



def run_generals(orderset):
    for order in orderset: 
        generals(order)
        print ""           #last newline needed>



def generals(order):
    m = int(order[0])
    
    generals = [] 
    for i in range(len(order[1])): 
        generals.append( General(i, order[1][i]) )   #create general list 
        General.nodeCount += 1

    if order[2] == "ATTACK":
        generals[0].ordict['_'] = orders.attack  #initialize/seed alpha-commander's knowledge of own command; 
    elif order[2] == "RETREAT":                  # '_' is what I like to call the "god prefix"
        generals[0].ordict['_'] = orders.retreat
    else:
        print "Not a valid initial order for the commander" 
        exit(0)


    _generals_h('_', m, generals[0], generals[1:])

    #check results
    for gen in generals[1:]:
        gen.printgen('_0',generals[1:])
    



def _generals_h(prefix, m, commander, generals): 
    newfix = ''.join([prefix,str(commander.id)]) #create new prefix to convey to lnts who Com. is talking about.

    if m == 0:
        commander.tell_orders(generals,prefix)

    else: 
        commander.tell_orders(generals, prefix)
        
        #exchange order knowledge
        for gen in generals:
            cpy = copy.copy(generals) #Shallow copy 
            cpy.remove(gen) 
            _generals_h(newfix,m-1,gen, cpy) 
            
        #do majority:
        for gen in generals:
            cpy = copy.copy(generals) #Shallow copy 
            cpy.remove(gen)
            gen.ordict[newfix] = majority(gen, cpy , newfix) 
            gen.order = gen.ordict[newfix]
       
    return 




def majority(general, bros, prefix):

    ordlist = []
    attackcount = 0
    retreatcount = 0

    for gen in bros: 
        key = prefix + str(gen.id)
        value = general.ordict[key]

        if value == orders.attack:
            attackcount += 1
            ordlist.append((key, "attack"))
        elif value == orders.retreat: 
            ordlist.append((key,"retreat"))
            retreatcount += 1
        elif value == orders.tie:
            ordlist.append((key,"tie"))

    #count yourself. apparently needed. 
    key = prefix + str(general.id)
    value = general.ordict[key]
    
    if value == orders.attack:
            attackcount += 1
            ordlist.append((key, "attack"))
    elif value == orders.retreat: 
            retreatcount += 1
            ordlist.append((key, "retreat"))
    elif value == orders.tie:
            ordlist.append((key,"tie"))


    if attackcount > retreatcount:
        if verbose:
            print "general " + str(general.id) + " used ATTACK for prefix " + prefix
            print "orders:"
            print ordlist
            print " "    
        return orders.attack
    elif retreatcount > attackcount:
        if verbose:
            print "general " + str(general.id) + " used RETREAT for prefix " + prefix
            print "orders:"
            print ordlist
            print " "  
        return orders.retreat
    elif retreatcount == attackcount:
        if verbose:        
            print "general " + str(general.id) + " used TIE for prefix " + prefix
            print "orders:"
            print ordlist
            print " "
        return orders.tie
    else:
        print "math failed."
        exit(1)



#######################

run_generals( readorders() )