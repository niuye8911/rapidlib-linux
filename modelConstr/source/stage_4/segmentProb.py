from Classes import *
#construct variables
def getSegments(samples,mode):
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


#construct costFunction based on modes
# mode=="piece-wise" || mode == "quadratic"
def costFunction(samples, mode):
    if mode=="piecewise":
        #generate piece wise linear cost fuctions
        return ""