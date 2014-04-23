#from enum import Enum

class orders:
    attack = 1
    retreat = 2
    tie = 3
    


class Node:
    'general node-processor class' 
    nodeCount = 0
    
    def __init__(self,id, loyalty):
        self.id = id
        self.loyal = loyal #bool
        node.nodeCount += 1
        self.order = orders.retreat #default to retreat?



def readorders(): #reads in orders and returns a list of them
    orderset = []
    
    print "Input Togography:"

    inputs = raw_input()
    while inputs.split(" ")[1] != "END":
        orderset.append(inputs.split(" "))
        inputs = raw_input()

    return orderset

def generals(orderset):
    for order in orderset: 
        _generals_h(order)

def _generals_h(order):
    m = order[0]
    
    generals = [] 
    for i in range(len(order[1])): 
        generals.append( General(i, order[1][i]) )
        orders.nodeCount += 1

    if order[2] == "ATTACK":
        generals[0].orders = orders.attack  
    elif order[2] == "RETERAT":
        generals[0].orders = orders.retreat
    else
        print "Not a valid initial order for the commander" 
        exit(0)

#time to actually do the algorithm    