import  os
import requests
from configClass import RSDGNode
from configClass import RAPIDConfig

# def readrsdg(rsdg):
#     res = {}
#     f = open(rsdg,'r')
#     for line in f:
#         col = line.split()
#         name = col[0]
#         res[name] = []
#         for i in range (1,len(col)):
#             res[name].append(float(col[i]))
#     return res

def solveAndPopulate(service_levels, PRINT):
    url = "http://algaesim.cs.rutgers.edu/solver/index.php"
    file = {'upload_file[]' : ('hello', open("./problem.lp", 'rb'))}
    response = requests.post(url, files = file)
    result = response.text
    item = result.split("\\n")
    maxsol = open("max.sol", 'w')
    for i in item:
	if i=="\"":
		continue
	maxsol.write(i)
	maxsol.write("\n")
    maxsol.close()
    resFile = open("max.sol",'r')
    rsdg = {}
    for line in resFile:
        col = line.split()
        if len(col)==2:# a result
            nodeName = col[0]
            val = float(col[1])
            nodeName = nodeName.split('_')
            if not(len(nodeName)==2):
                rsdg[col[0]] = []
                rsdg[col[0]].append(val)
                continue
            svcName = nodeName[0]
            lvl = int(nodeName[1])
            #add to rsdg
            # if the service is first seen
            if not(rsdg.has_key(svcName)):#not found service
                rsdg[svcName] = []
                lvlNum = service_levels[svcName]
                for i in range(0,lvlNum):
                    rsdg[svcName].append(-1)
            # add the current result to the rsdg
            print svcName, lvl-1
            rsdg[svcName][lvl-1] = val
    resFile.close()
    if(PRINT):printRSDG(rsdg,True)
    return rsdg

def printRSDG(rsdg,output):
    rsdgF = open("rsdg",'w')
    for i in rsdg:
        strg = ""
        lvls = rsdg[i]
        for lvl in lvls:
            strg+=str(lvl) + " "
        rsdgF.write(i + " "+ strg + "\n")
        if output: print (str(i) + ":"+ strg + "\n")

# generate the optimization problem that tries to find a value distribution that minimizes the error
def genProblem(service_levels, configs):
    prob = open("problem.lp",'w')
    #write obj
    prob.write("Minimize\nerr\n\n")
    #write order constraint
    constraints = genConstraintsFromConfigs(configs)
    prob.write("Subject To\n")
    for s in service_levels:
        lvls = service_levels[s]
        for i in range(1,lvls):
            prob.write(s + "_" + str(i) + " - " + s + "_" + str(i+1) + " > 1\n")
    prob.write("\n")
    for c in constraints:
        prob.write(c)
        prob.write("\n")

    # if a node does not occur, we assume it's around the middle of the neighboring nodes
        #set up the not_touched nodes list
    not_touched = {}
    for service in service_levels:
        lvl = service_levels[service]
        not_touched[service] = []
        for i in range(1,lvl+1):
            not_touched[service].append(i)
        # remove the visited nodes
    for config in configs:
        # each config is a RAPIDConfig
        nodes = config.get_nodes()
        for node in nodes:
            node_service_name = node.service
            node_level = node.level
            if node_level in not_touched[node_service_name]:
                not_touched[node_service_name].remove(node_level)
        # from now on, all entries in not_touched contains the not touched nodes
    # write those untouched nodes to file
    for service in not_touched:
        for lvl in not_touched[service]:
            if lvl == 1 or lvl == service_levels[service]:
                # if it's the top of bottom node, don't do anything
                continue
            # print to file
            cur_node = service + "_" + str(lvl)
            top_neighbour = service + "_" + str(lvl-1)
            bot_neighbour = service + "_" + str(lvl+1)
            linear_constraint = top_neighbour + " + " + bot_neighbour + " - 2 " + cur_node + " = 0"
            prob.write(linear_constraint)
            prob.write("\n")

    #write end
    prob.write("End")
    prob.close()


# generate a list of constraints from a list of configs
def genConstraintsFromConfigs(configs):
    result_constraints = []
    for config in configs:
        constraint, dual_constraint = genConstraintFromConfig(config)
        result_constraints.append(constraint)
        result_constraints.append(dual_constraint)
    return result_constraints


# return a constraint and a dual-constraint for each configuration
def genConstraintFromConfig(c):
    """It returns two strings, representing the constraint pair of a config in observed file"""
    constraint = ""
    dualConstraint = ""
    nodes = c.get_nodes()
    num_of_nodes = len(nodes)
    for i in range(0, num_of_nodes):
        node = nodes[i]
        constraint += node.print_in_constraint()
        dualConstraint += node.print_in_constraint()
        if i<num_of_nodes-1:# not the last node
            constraint += " + "
            dualConstraint += " + "
        else:
            constraint += " >= " + c.get_cost()
            dualConstraint += " - " + c.get_cost() + " err <= " + c.get_cost()
    return constraint, dualConstraint

# return an array of RAPIDConfig's and a map that indicates how many layers are there in a particular service
def generateConfigsFromTraining(fileName):
    """Return a list of RAPIDConfigs objects that contains the ndoe selected and their cost"""
    factFile = open(fileName,'r')
    configs = []
    service_levels = {} # a map that the entry is the service name and the value is the total configs
    for line in factFile:
        col = line.split(',')
        lineLength = len(col)
        name = ""
        lvl = -1
        nodes = []
        for i in range(0,lineLength):
            if i==lineLength-1:
                cost = col[i]
                configs.append(RAPIDConfig(nodes, cost))
                continue
            cur = col[i]
            if not(cur.isdigit()):#if it's service name
                name = cur
            else:
                lvl = int(cur)
                nodes.append(RSDGNode(name, lvl))
                # create a map that maintains the number of layers in a service
                if service_levels.has_key(name):
                    if service_levels[name] < lvl:
                        service_levels[name] = lvl
                else:
                    service_levels[name] = lvl
    factFile.close()
    return configs, service_levels

def parseKF(KF):
    kf = open(KF,'r')
    kfc = ""
    for line in kf:
        col = line.split()
        kfc += col[0] + " = " + col[1] + '\n'
    return kfc;
