from Classes import *
from contigous import *

# generate a cont problem
def generateContProblem(observed,partitions,mode):
    if mode=="quad":
        # write the observation to an observed file
        observed.printProfile("observed.csv")
        genContProblem("observed.csv","quad")
    else:
        # get the segments
        segments = getSegments(partitions)
        # get the variables
        variables = getVariables(partitions)
        return

#construct variables
def getSegments(samples):
    segments = {}
    for knob in samples:
        name = knob
        points = samples[name]
        segments[name] = []
        id = 0
        min = points[0]
        for i in range(1,len(points)):
            segname = name + "_"+str(id)
            max = points[i]
            segments[name].append(Segment(segname,name,min,max))
            min = points[i]
    return segments

# construct variables
def getVariables(partitions):
    pass

#construct costFunction based on modes
# mode=="piece-wise" || mode == "quadratic"
def costFunction(samples, mode):
    if mode=="piecewise":
        #generate piece wise linear cost fuctions
        return ""