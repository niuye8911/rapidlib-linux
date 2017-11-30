# Tools needed for generating contigous RSDG
def genContProblem(fact):
    prob = open("contproblem.lp", 'w')
    constraints, num, paras = readContFactAndGenConstraint(fact)
    # write obj
    obj = "[ "
    for i in range(1,num+1):
        obj += "err"+str(i) + " ^ 2"
        if not (i==num):
            obj += " + "
    obj += " ]\n"
    #prob.write("Minimize\n[ err ^ 2 ]\n\n")
    prob.write("Minimize\n")
    prob.write(obj + "\n")
    # write constraint
    prob.write("Subject To\n")
    for c in constraints:
        prob.write(c)
    return paras

def getContRSDG(paras):
    result = open("max.sol", 'r')
    rsdg = open("rsdgcont",'w')
    for line in result:
        col = line.split()
        if not (len(col) == 2):
            continue
        name = col[0]
        val = col[1]
        if not (name in paras):
            continue
        rsdg.write(name + " " + val + "\n")
    rsdg.close()


def readContFactAndGenConstraint(fact):
    services = set()
    constraints = []
    paras = set()
    num = 0
    f = open(fact, 'r')
    for line in f:
        col = line.split(',')
        length = len(col)
        name = ""
        lvl = -1
        constraint = ""
        for i in range (0,length):
            if i == length-1:
                #the last column which is the cost
                cost = float(col[i])
                constraint += "err"+str(num+1)+" = "+str(cost)+"\n"
                constraints.append(constraint)
                constraint = ""
                continue
            cur = col[i]
            if not (cur.isdigit()): # this is a service name
                name = cur
                services.add(name)
            else:
                value = float(cur)
                # write the 2-order constraint
                o2para = name+"_2"
                o1para = name+"_1"
                cpara = name + "_c"
                paras.add(o2para)
                paras.add(o1para)
                paras.add(cpara)
                constraint +=  str(value*value) + " " + o2para + " + " + str(value) + " " + o1para + " + " + cpara + " + "
        num += 1

    return constraints,num, paras



