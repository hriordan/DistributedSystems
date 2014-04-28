
class orders:
    attack = 1
    retreat = 2
    tie = 3
    


class Node:
    'general node-processor class' 
    nodeCount = 0
    
    def __init__(self, id, loyalty):
        self.id = id

        if loyalty == 'L':
            self.loyal = True
        else:
            self.loyal = False

        node.nodeCount += 1
        
        self.order = orders.retreat #default to retreat?
        
        self.ordict = {}


    def __eq__(self, other):
        if self.id == other.id:
            return True
        else:
            return False


    def tell_orders(self, generals, prefix):
        key = ''.join([prefix,self.id])
        self.ordict[key] = self.ordict[prefix] #"tell yourself what you are talking about"

        if self.loyal == True: 
            for gen in generals:
                gen.ordict[key] = self.ordict[key]
        else: #Traitor! 
            for gen in generals:
                if gen.id % 2 == 0: 
                    if self.ordict[key] == orders.retreat:
                        gen.ordict[key] = orders.attack
                    else:
                        gen.ordict[key] = orders.retreat
                else:
                    gen.ordict[key] = self.ordict[key] 



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



def generals(order):
    m = order[0]
    
    generals = [] 
    for i in range(len(order[1])): 
        generals.append( General(i, order[1][i]) )   #create general list 
        orders.nodeCount += 1

    if order[2] == "ATTACK":
        generals[0].ordict['_'] = orders.attack  #initialize/seed alpha-commander's knowledge of own command 
    elif order[2] == "RETREAT":
        generals[0].ordict['_'] = orders.retreat
    else:
        print "Not a valid initial order for the commander" 
        exit(0)

    _generals_h('_', m, generals[0], generals[2:])

    #check results
    for gen in generals:
        print str(gen.id) + "is doing " + str(gen.orders)




def _generals_h(prefix, m, commander, generals): #whatdo
    
    newfix = ''.join([prefix,commander.id])



    if m == 0:
        commander.tell_orders(generals,prefix)
        #return generals 

    else: 
        commander.tell_orders(generals, prefix)

        #exchange order knowledge
        for gen in generals:
            _generals_h(newfix,m-1,gen,generals.remove(gen)) #will the generals argument be a local copy? please say yes

        #do majority:
        for gen in generals:
            gen.ordict[prefix] = majority(gen, generals.remove(gen), prefix) #again, ensure the scope here. 
            gen.orders = gen.ordict[prefix]

        #return generals
    return 




def majority(general, bros, prefix):
    attackcount = 0
    retreatcount = 0


    for gen in bros: 
        key = prefix + str(gen.id)
        value = general.ordict[key]

        if value == orders.attack:
            attackcount += 1
        else: 
            retreatcount += 1

    if attackcount > retreatcount:
        return orders.attack
    elif retreatcount > attackcount:
        return orders.retreat
    else:
        return orders.tie



######################3

run_generals( readorders() )
