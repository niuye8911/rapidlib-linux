from stage_1.training import *
from Classes import *
from representset import *
from segmentProb import *
# contains functions to compute the representative list of a RSDG, given the fact profile
def constructRSDG(gt, knob_samples, threshold, knobs, PRINT,model):
    # gT is a dictionary where entry is the config and value is hte cost
    # profile_configs is the structured configuration
    # segmentation level
    seglvl = 0
    # initial error rate set to 100%
    error = 1.0
    while error>=threshold:
        if seglvl >= 4:
            print "Reached Highest Segmentation Granularity"
            break
        seglvl += 1
        partitions = partition(seglvl,knob_samples)
        observed_profile = retrieve(partitions, gt, knobs)
        costrsdg,mvrsdg = populate(observed_profile,partitions,model)
        error = compare(costrsdg,gt,False,model)
    if PRINT:
        compare(costrsdg,gt,True)
        print "Granulatiry = "+ str(seglvl)
    return costrsdg,mvrsdg

# given a partion level, return a list of configurations
def partition(seglvl, knob_samples):
    partitions = {}
    #seglvl indicate the number of partition lvl on each knob
    for knob in knob_samples:
        val_range = knob_samples[knob]
        length = len(val_range)
        partitions[knob] = []
        max = length-1
        min = 0
        # determine the step size
        num_of_partitions = 2**(seglvl-1)
        step = length / num_of_partitions - 1
        if step<1:
            step = 1
        for i in range(min,max+1,step):
            partitions[knob].append(val_range[i])
        #extend the last one to the end
        length = len(partitions[knob])
        partitions[knob][length-1]=val_range[max]
    return partitions

# given a partition list, retrieve the data points in ground truth
# return a profile by observation
def retrieve(partitions, gt, knobs,COST=False):
    observed_profile = Profile()
    final_sets = set()
    # partitions contains a dictionary of all knob samples
    for knob in partitions:
        samples = partitions[knob]
        single_set = []
        for sample in samples:
            single_set.append(Config(knobs.getKnob(knob),sample))
        final_sets.add(frozenset(single_set))
    product = crossproduct(final_sets)
    flatted_observed = flatAll(product)
    for config in flatted_observed:
        configuration = Configuration()
        configuration.addConfig(config)
        # filter out the invalid config, invalid if not present in groundTruth
        if not gt.hasEntry(configuration):
            continue
        costval = gt.getCost(configuration)
        mvval = gt.getMV(configuration)
        observed_profile.addCostEntry(configuration, costval)
        observed_profile.addMVEntry(configuration,mvval)
    return observed_profile

# given an observed profile, generate the continuous problem and populate the rsdg
def populate(observed,partitions,model):
    # get the segments
    segments, seg_values, segconst,inter_coeff= generateContProblem(observed,partitions,model)
    costrsdg = solveAndPopulateRSDG(segments, seg_values, segconst, inter_coeff)
    system("mv ./debug/max.sol ./debug/maxcost.sol")
    system("mv ./debug/fitting.lp ./debug/fittingcost.lp")
    #  solve and retrieve the result
    segments_mv, seg_values_mv, segconst_mv, inter_coeff_mv = generateContProblem(observed, partitions, model,False)
    mvrsdg = solveAndPopulateRSDG(segments_mv, seg_values_mv, segconst_mv, inter_coeff_mv, False)
    system("mv ./debug/max.sol ./debug/maxmv.sol")
    system("mv ./debug/fitting.lp ./debug/fittingmv.lp")
    return costrsdg,mvrsdg

def compare(rsdg,groundTruth,PRINT):
    outfile = None
    if PRINT:
        outfile = open("outputs/modelValid.csv",'w')
    error = 0.0
    count = 0
    for configuration in groundTruth.configurations:
        count += 1
        rsdgCost = rsdg.calCost(configuration)
        measurement = groundTruth.getCost(configuration)
        error += abs(measurement-rsdgCost)/measurement
        if PRINT:
            for config in configuration.retrieve_configs():
                outfile.write(config.knob.set_name)
                outfile.write(",")
                outfile.write(str(config.val))
                outfile.write(",")
            outfile.write(str(measurement))
            outfile.write(",")
            outfile.write(str(rsdgCost))
            outfile.write(",")
            outfile.write(str((measurement-rsdgCost)/measurement))
            outfile.write("\n")
    if PRINT:
        outfile.close()
        print error/count
    return error / count
