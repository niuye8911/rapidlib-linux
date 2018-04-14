from Classes import *
from contigous import *
from stage_1.training import *

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
        seg_indicators, seg_values, knob_values = getVariables(partitions,segments)
        # get cost functions
        obj = errorFunction(segments,observed,mode)
        # get the constraints
        costConstraints, segConstraints, errors = genConstraints(segments,observed, mode)
        # get the bounds
        intBounds, floatBounds = genBounds(seg_indicators, seg_values, knob_values, errors)
        # beatutifyProblem
        beautifyProblem(obj,costConstraints,segConstraints,intBounds,floatBounds,seg_indicators)
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
            segname = name
            max = points[i]
            seg = Segment(segname,name,min,max)
            seg.setID(id)
            segments[name].append(seg)
            id+=1
            min = points[i]
    return segments

# construct variables
def getVariables(partitions,segments):
    seg_indicators = set()
    seg_values = set()
    knob_values = set()
    for knob in partitions:
        name = knob
        knob_values.add(name)
    for segment in segments:
        knob_name = segment
        knob_segs = segments[segment]
        for knob_seg in knob_segs:
            seg_indicators.add(knob_seg.printID())
            seg_values.add(knob_seg.printVar())
    return seg_indicators,seg_values,knob_values

# generate the error function
def errorFunction(segments, observed,mode):
    observation_num = len(observed.profile_table)
    obj = ""
    quadobj = "[ "
    for i in range(0, observation_num):
        obj += "-2 err" + str(i)
        quadobj += "err" + str(i) + " ^ 2"
        if not (i == observation_num-1):
            obj += " + "
            quadobj += " + "
    quadobj += " ]\n"
    obj += " + " + quadobj
    return obj

#construct costFunction based on modes
# mode=="piece-wise" || mode == "quadratic"
def costFunction(segments,observed, mode):
    costFunction = ""
    if mode=="piecewise":
        #generate piece wise linear cost fuctions
        first_order_coeff = 0
        const_coeff = 0
        # first order
        for configuration in observed.configurations:
            cost = observed.getCost(configuration)
            for config in configuration.retrieve_configs():
                knob_name = config.knob.set_name
                knob_val = config.val
                for seg in segments[knob_name]:
                    costFunction+=str(knob_val) + " " + seg.printVar() + " + "+str(knob_val) + " + "+ seg.printID() + " + "
            costFunction=costFunction[:-3]
        print costFunction
    return costFunction

def genConstraints(segments,observed, mode):
    if mode == "piecewise":
        # generate piece wise linear cost fuctions
        costConstraints = set()
        segConstraints = set()
        errors = set()
        # generate the cost Constraints
        for configuration in observed.configurations:
            err_id = 0
            err_name= "err"+str(err_id)
            err_id+=1
            errors.add(err_name)
            costVal = observed.getCost(configuration)
            fall_within_segs = {}
            for config in configuration.retrieve_configs():
                knob_name = config.knob.set_name
                knob_val = config.val
                #seg_sum = ""
                for seg in segments[knob_name]:
                    if knob_val<seg.min or knob_val > seg.max:
                        continue
                    if not knob_name in fall_within_segs:
                        fall_within_segs[knob_name] = []
                    fall_within_segs[knob_name].append(seg)
                    # generate the seg Constraints
                    #posSegConstraint = seg.printID() + " = 1 -> " + seg.printVar() + " = " + knob_name
                    #negSegConstraint = seg.printID() + " = 0 -> " + seg.printVar() + " = 0"
                    #seg_sum += seg.printID() + " + "
                    #segConstraints.add(posSegConstraint)
                    #segConstraints.add(negSegConstraint)
                #seg_sum = seg_sum[:-3]
                #segConstraints.add(seg_sum+ " = 1")
                # get all combinations of fall_within_segs
            flatted_segs = getFlattedSeg(fall_within_segs)
            costEstimates = []
            for flatted_seg_list in flatted_segs:
                costEstimate = ""
                for flatted_seg in flatted_seg_list:
                    costEstimate += str(knob_val) + " " + flatted_seg.printVar() + " + " + flatted_seg.printConst() + " + "
                costEstimate = costEstimate[:-3]
                costEstimates.append(costEstimate)
            # generate inter-service
            inter_cost = ""
            if not len(configuration.retrieve_configs())==1:
                configs = configuration.retrieve_configs()
                total_num = len(configs)
                for i in range(0,total_num-1):
                    s1 = configs[i].knob.set_name
                    s1_val = configs[i].val
                    for j in range(1,total_num):
                        s2 = configs[j].knob.set_name
                        s2_val = configs[j].val
                        inter_cost+=str(s1_val * s2_val) + " " + s1+"_"+s2 + " + "
                inter_cost = inter_cost[:-3]
            for costEstimate in costEstimates:
                costEstimate += inter_cost
                constraint = costEstimate + " + " + err_name + " = " + str(costVal)
                costConstraints.add(constraint)
    return costConstraints,segConstraints,errors

# get a combination of cost estimates
def getFlattedSeg(fall_within_segs):
    result = []
    finalsets = set()
    for knob in fall_within_segs:
        singleset = frozenset(fall_within_segs[knob])
        finalsets.add(singleset)
    prod = crossproduct(finalsets)
    flatted = flatAll(prod)
    return flatted

def genBounds(seg_indicators, seg_values, knob_values, errors):
    integerBounds = set()
    floatBounds = set()
    # segIDs
    for seg_indicator in seg_indicators:
        bound = seg_indicator + " <= 1"
        integerBounds.add(bound)
    for seg_value in seg_values:
        floatBound = "-99999 <= " + seg_value + " <= 99999"
        floatBounds.add(floatBound)
    for knob_value in knob_values:
        floatBound = "-99999 <= " + knob_value + " <= 99999"
        floatBounds.add(floatBound)
    for error in errors:
        floatBound = "-99999 <= " + error + " <= 99999"
        floatBounds.add(floatBound)
    return integerBounds,floatBounds

def beautifyProblem(obj, costConstraints, segConstraints, intBounds, floatBounds,seg_indicators):
    probfile = open("./fitting.lp",'w')
    probfile.write("Minimize\n")
    probfile.write(obj)
    probfile.write("\nSubject To\n")
    for costConstraint in costConstraints:
        probfile.write(costConstraint)
        probfile.write("\n")
    for segConstraint in segConstraints:
        probfile.write(segConstraint)
        probfile.write("\n")
    probfile.write("Bounds\n")
    for bound in intBounds:
        probfile.write(bound + "\n")
    for bound in floatBounds:
        probfile.write(bound + "\n")
    probfile.write("Integers\n")
    for seg in seg_indicators:
        probfile.write(seg + "\n")
    probfile.close()