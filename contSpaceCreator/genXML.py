from Service import Node
from Service import Service
import os
import datetime as dt
problem = "" #the final problem being generated

def genHeader():
    global problem
    problem = problem + "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<resource>\n"

def genNode(node):
    nodeBlock = ""
    nodeBlock += "\t\t<basicnode>\n\t\t\t<nodename>"+node.get_name()+"</nodename>\n"
    nodeBlock += "\t\t\t<nodecost>"+str(node.get_cost())+"</nodecost>\n"
    nodeBlock += "\t\t\t<nodemv>" + str(node.get_mv()) + "</nodemv>\n"
    nodeBlock += "\t\t</basicnode>"
    return nodeBlock

def genService(service):
    serviceBlock = ""
    serviceBlock += "<service>\n"
    serviceBlock += "<servicename>" + service.get_name() + "</servicename>\n"
    for node in service.get_nodes():
        serviceBlock += "\t<servicelayer>\n"
        serviceBlock += genNode(node)
        serviceBlock += "\n\t</servicelayer>\n"
    return serviceBlock

def genEnd():
    global problem
    problem += "</service></resource>"

def genProblem(name, serviceList):
    global problem
    genHeader()
    """service list contains a list of services, each service contains the list of nodes"""
    for service in serviceList:
        problem += genService(service)
    genEnd()
    file = open(name, 'w')
    file.write(problem)
    file.close()

def testSwaption():
    global problem
    rangeLow = 100*1000
    rangeHigh = 1000*1000
    steps = range (10, 110, 10)
    steps = [100000]
    report = open("report", 'w')
    for step in steps:
        # reset everything
        problem = ""
        os.system("rm swaption.xml")
        os.system("rm MAX.lp")
        numOfItr = Service("num")
        for i in range(rangeLow,rangeHigh,step):
            new_node = Node("num"+str(i), 10000*1000.0/i, 1000*1000/i)
            numOfItr.add_node(new_node)
        serviceList = []
        serviceList.append(numOfItr)
        genProblem("swaption.xml", serviceList)
        os.system("./test")
        n1 = dt.datetime.now()
        os.system("gurobi_cl ResultFile=max.sol MAX.lp")
        n2 = dt.datetime.now()
        elapsedTime = (n2 - n1 ).microseconds
        elapsedTime = elapsedTime/1000
        print "Used time::" + str(elapsedTime)
        report.write(str(elapsedTime))
        report.write("\n")

    report.close()

testSwaption()