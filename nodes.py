import copy

class orders:
    attack = 1
    retreat = 2
    tie = 3
    


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
        
        self.order = orders.retreat #default to retreat?
        
        self.ordict = {}  #global orders dictionary consisting of a prefix keys and order values
                          #e.g. '013': 'attack' ==>3 said 1 said 0 ordered attack 

    def __eq__(self, other):
        if self.id == other.id:
            return True
        else:
            return False


    def tell_orders(self, generals, prefix):
        
        verbose = 0

        key = ''.join([prefix, str(self.id)])
        
        #if self.id == 2:
         #   verbose = 1
        
        if verbose:
            print key
            print prefix
            print self.ordict
            print self.ordict[prefix]
           
        self.ordict[key] = self.ordict[prefix] #"tell yourself what you are talking about" --redundant, but helpful in passing orders btw layers

        if self.loyal == True: 
            for gen in generals:
                gen.ordict[key] = self.ordict[key]
                if verbose:
                    print "I told general " + str(gen.id) + " to " + str(self.ordict[key]) + " for prefix" + prefix

        else: #Traitor! 
            for gen in generals:
                if gen.id % 2 == 0: 
                    if self.ordict[key] == orders.retreat:
                        gen.ordict[key] = orders.attack
                    else:
                        gen.ordict[key] = orders.retreat
                else:
                    gen.ordict[key] = self.ordict[key] 
    


    def printgen(self, prefix, others):
        orderlist = ""
        orderlist += str(self.ordict[prefix]) + " " # original order from commander 

        for gen in others: 
            if self == gen: #will it blend?
                orderlist += " " 
            else:
                key = prefix + str(gen.id)
                if gen.ordict[key] == orders.attack:
                    orderlist += "A"
                elif gen.ordict[key] == orders.retreat:
                    orderlist += "R"
                elif gen.ordict[key] == orders.tie:
                    orderlist += "-"
                else:
                    orderlist += "%" #error 

        if self.order == orders.attack:
            orderlist += " ATTACK"
        elif self.order == orders.retreat:
            orderlist += " RETREAT"
        elif self.order == orders.tie:
            orderlist += " TIE"
        else:
            print "How did you get an order other than the default 3? " + str(gen.order)
            exit(1)

        print orderlist




def readorders(): #reads in orders and returns a list of them
    orderset = []
    
    print "Input Togography:"

    inputs = raw_input()
    while inputs.split(" ")[1] != "END":
        orderset.append(inputs.split(" "))
        inputs = raw_input()

    return orderset



def run_generals(orderset):
    for order in orderset: 
        generals(order)
        print ""



def generals(order):
    m = int(order[0])
    
    generals = [] 
    for i in range(len(order[1])): 
        generals.append( General(i, order[1][i]) )   #create general list 
        General.nodeCount += 1

    if order[2] == "ATTACK":
        generals[0].ordict['_'] = orders.attack  #initialize/seed alpha-commander's knowledge of own command 
    elif order[2] == "RETREAT":
        generals[0].ordict['_'] = orders.retreat
    else:
        print "Not a valid initial order for the commander" 
        exit(0)


    #print generals[0].loyal
      
    _generals_h('_', m, generals[0], generals[1:])

    #check results
    for gen in generals[1:]:
        gen.printgen('_0',generals[1:])
    



def _generals_h(prefix, m, commander, generals):
    
    newfix = ''.join([prefix,str(commander.id)]) #create new prefix to convey to lnts 

    if m == 0:
        commander.tell_orders(generals,prefix)
        #return generals 

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
            gen.ordict[newfix] = majority(gen, cpy , newfix) #again, ensure the scope here. 
            gen.order = gen.ordict[newfix]

       
    return 




def majority(general, bros, prefix):

    ordlist = []
    attackcount = 0
    retreatcount = 0

    #doublecheck: need to use own value for majority vote? 
    for gen in bros: 
        key = prefix + str(gen.id)
        value = general.ordict[key]

        if value == orders.attack:
            attackcount += 1
            ordlist.append((key, "attack"))
        elif value == orders.retreat: 
            ordlist.append((key,"retreat"))
            retreatcount += 1

    #count yourself. apparently needed? 
    key = prefix + str(general.id)
    value = general.ordict[key]
    
    if value == orders.attack:
            attackcount += 1
            ordlist.append((key, "attack"))
    elif value == orders.retreat: 
            retreatcount += 1
            ordlist.append((key, "retreat"))

    if attackcount > retreatcount:
        """print "general " + str(general.id) + " used ATTACK for prefix " + prefix
        print "orders:"
        print ordlist
        print " " """   
        return orders.attack
    elif retreatcount > attackcount:
        """print "general " + str(general.id) + " used RETREAT for prefix " + prefix
        print "orders:"
        print ordlist
        print " "  """
        return orders.retreat
    elif retreatcount == attackcount:
        """  print "general " + str(general.id) + " used TIE for prefix " + prefix
        print "orders:"
        print ordlist
        print " " """
        return orders.tie
    else:
        print "math failed."
        exit(1)



######################3

run_generals( readorders() )
