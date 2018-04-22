from Classes import *
from contigous import *
from stage_1.training import *
from os import system

# generate a cont problem
def generateContProblem(observed,partitions,mode):
    if mode=="quad":
        # write the observation to an observed file
        genContProblem("observed.csv","quad")
    else:
        observed.printProfile("./outputs/observed.csv")
        # get the segments
        segments = getSegments(partitions)
        # get the variables
        seg_indicators, seg_values,segconst, knob_values = getVariables(partitions,segments)
        # get the constraints
        costConstraints, segConstraints, errors,inter_coeff = genConstraints(segments,observed, mode)
        # get obj functions
        obj = errorFunction(errors)
        # get the bounds
        intBounds, floatBounds = genBounds(seg_indicators, seg_values, segconst, knob_values, errors)
        # beatutifyProblem
        beautifyProblem(obj,costConstraints,segConstraints,intBounds,floatBounds,seg_indicators)
    return segments, seg_values, segconst,inter_coeff

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
    seg_const  = set()
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
            seg_const.add(knob_seg.printConst())
    return seg_indicators,seg_values,seg_const,knob_values

# generate the error function
def errorFunction(errors):
    num = len(errors)
    obj = ""
    quadobj = "[ "
    for i in range(0, num):
        #obj += "-2 " + errors[i]
        quadobj += errors[i] + " ^ 2"
        if not (i == num-1):
            #obj += " + "
            quadobj += " + "
    quadobj += " ]\n"
    #obj += " + " + quadobj
    obj += quadobj
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
    return costFunction

def genConstraints(segments,observed, mode):
    if mode == "piecewise":
        # generate piece wise linear cost fuctions
        costConstraints = set()
        segConstraints = set()
        inter_coeff = set()
        errors = []
        # generate the cost Constraints"
        err_id = 0
        for configuration in observed.configurations:
            costVal = observed.getCost(configuration)
            fall_within_segs = {}
            for config in configuration.retrieve_configs():
                knob_name = config.knob.set_name
                knob_val = config.val
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
                    knob_val = configuration.getCost(flatted_seg.knob_name)
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
                    for j in range(i+1,total_num):
                        s2 = configs[j].knob.set_name
                        s2_val = configs[j].val
                        inter_cost+=str(s1_val * s2_val) + " " + s1+"_"+s2 + " + "
                        inter_coeff.add(s1+"_"+s2)
                inter_cost = inter_cost[:-3]
            for costEstimate in costEstimates:
                if not inter_cost == "":
                    costEstimate += " + " + inter_cost
                err_name = "err" + str(err_id)
                err_id += 1
                errors.append(err_name)
                constraint = costEstimate + " + " + err_name + " = " + str(costVal)
                costConstraints.add(constraint)
    return costConstraints,segConstraints,errors,inter_coeff

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

def genBounds(seg_indicators, seg_values, segconst,knob_values, errors):
    integerBounds = set()
    floatBounds = set()
    # segIDs
    for seg_indicator in seg_indicators:
        bound = seg_indicator + " <= 1"
        integerBounds.add(bound)
    #for seg_value in seg_values:
    #    floatBound = "-99999 <= " + seg_value + " <= 99999"
    #    floatBounds.add(floatBound)
    #for seg_value in segconst:
    #    floatBound = "-99999 <= " + seg_value + " <= 99999"
    #    floatBounds.add(floatBound)
    #for knob_value in knob_values:
    #    floatBound = "-99999 <= " + knob_value + " <= 99999"
    #    floatBounds.add(floatBound)
    for error in errors:
        floatBound = "-99999 <= " + error + " <= 99999"
        floatBounds.add(floatBound)
    return integerBounds,floatBounds

def beautifyProblem(obj, costConstraints, segConstraints, intBounds, floatBounds,seg_indicators):
    probfile = open("./debug/fitting.lp",'w')
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

def solveAndPopulateRSDG(segments, seg_values, segconst,inter_coeff):
    system("gurobi_cl OutputFlag=0 LogToFile=gurobi.log ResultFile=./debug/max.sol ./debug/fitting.lp")
    result = open("./debug/max.sol",'r')
    rsdg = pieceRSDG()
    # setup the knob table
    for knob in segments:
        rsdg.addKnob(knob)
        for seg in segments[knob]:
            rsdg.addSeg(knob,seg)
    for line in result:
        col = line.split()
        if not (len(col) == 2):
            continue
        name = col[0]
        val = float(col[1])
        if val > 9999 or val < -9999:
            print "found not derived value", name, val
            if val > 0:
                val = 99999-val
            else:
                val = -99999-val
        if name in seg_values:
            # knob_id_V
            cols = name.split("_")
            knob_name = cols[0]
            id = cols[1]
            seglist = rsdg.knob_table[knob_name]
            for seg in seglist:
                segname = seg.printVar()
                if segname == name:
                    seg.setLinearCoeff(val)
                    continue
        if name in segconst:
            # knob_id_V
            cols = name.split("_")
            knob_name = cols[0]
            id = cols[1]
            seglist = rsdg.knob_table[knob_name]
            for seg in seglist:
                segname = seg.printConst()
                if segname == name:
                    seg.setConstCoeff(val)
                    continue
        if name in inter_coeff:
            cols = name.split("_")
            knob_a = cols[0]
            knob_b = cols[1]

            rsdg.addInterCoeff(knob_a, knob_b, val)
    rsdg.printRSDG()
    return rsdg


