# Tools needed for generating contigous RSDG
def genContProblem(fact):
    prob = open("contproblem.lp", 'w')
    constraints, num, paras = readContFactAndGenModConstraint(fact)
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
    services = {}
    constraints = [] #list of constraints
    paras = set() #set of parameters, o2, o1, and c for each service
    # added this for inter-relationship higher order constraint
    num = 0
    f = open(fact, 'r')
    for line in f:
        col = line.split(',')
        length = len(col)
        name = ""
        constraint = ""
        quadconstraint = "" # this is the inter-service relationship
        for i in range (0,length):
            if i == length-1:
                #the last column which is the cost
                cost = float(col[i])
                # at this point, "services" contains all the services being used in current observation
                # clean up the last "+"
                length = len(quadconstraint)
                quadconstraint = quadconstraint[:length-2]
                # append the quadconstraint to constraint
                # uncomment the line below to support quad terms
                constraint += quadconstraint
                constraint += " + "
                constraint += "err"+str(num+1)+" = "+str(cost)+"\n"
                constraints.append(constraint)
                #clear the constraint
                constraint = ""
                quadconstraint = ""
                services.clear()
                continue
            cur = col[i]
            if not (cur.isdigit()): # this is a service name
                name = cur
            else:
                value = float(cur)
                # add the inter-service relationship to the quad constraint
                for service in services:
                    inter_para = value * services[service]
                    quadconstraint += str(inter_para) + " " + name + "_" + service + " + "
                services[name] = value  # record the current value for this service
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

# A function that generates cost / qual function in a way that Gurobi understands
def readContFactAndGenModConstraint(fact):
    services = {}
    constraints = [] #list of constraints
    paras = set() #set of parameters, o2, o1, and c for each service
    # added this for inter-relationship higher order constraint
    num = 0
    f = open(fact, 'r')
    for line in f:
        col = line.split(',')
        length = len(col)
        involved_services = [] # a list of involved services
        constraint = ""
        quadconstraint = "" # this is the inter-service relationship
        for i in range (0,length):
            if i == length-1:
                constraint += " err"+str(num+1)+ " + "
                #the last column which is the cost
                cost = float(col[i])
                # construct the quadconstraint that has PSD property
                # first construct the Svc ^ 2
                #for service in involved_services:
                #    quadconstraint += str(services[service] * services[service]) + " " + service+"_o2 " + " + "
                # then construct the inter relation
                quadconstraint += " [ "
                for i in range(0,len(involved_services)-1):
                    cur_service = involved_services[i]
                    for j in range(i+1, len(involved_services)):
                        inter_service = involved_services[j]
                        quadterm = cur_service+"_"+inter_service
                        quadterm_t = inter_service+"_"+cur_service
                        val = services[cur_service]
                        val_inter = services[inter_service]
                        print(val,val_inter,2*val*val_inter)
                        quad_cons = str(val*val) + " " + quadterm + " ^ 2 + " + str(val_inter * val_inter) + " " + quadterm_t + " ^ 2 - " + str(2*val_inter*val) + " "+quadterm + " * " + quadterm_t + " + "
                        quadconstraint += quad_cons
                # clean the quad constraint
                length = len(quadconstraint)
                quadconstraint = quadconstraint[:length-2]
                quadconstraint += " ] "
                # append the quadconstraint to constraint
                constraint += quadconstraint
                #greater_constraint = constraint + " >= "+str(cost-0.1)+"\n"
                smaller_constraint = constraint + " <= " + str(cost + 0.1) + "\n"
                #constraints.append(greater_constraint)
                constraints.append(smaller_constraint)
                #clear the constraint
                constraint = ""
                quadconstraint = ""
                services.clear()
                involved_services = []
                continue
            cur = col[i]
            if not (cur.isdigit()): # this is a service name
                name = cur
                involved_services.append(name)
            else:
                value = float(cur)
                # add the inter-service relationship to the quad constraint
               # for service in services:
               #     inter_para = value * services[service]
               #     quadconstraint += str(inter_para) + " " + name + "_" + service + " + "
                services[name] = value  # record the current value for this service
                # write the 2-order constraint
               # o2para = name+"_2"
                o1para = name+"_1"
                cpara = name + "_c"
               # paras.add(o2para)
                paras.add(o1para)
                paras.add(cpara)
                constraint +=  str(value) + " " + o1para + " + " + cpara + " + "
        num += 1

    return constraints,num, paras

