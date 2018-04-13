from stage_1.training import *
from Classes import *
from representset import *
# contains functions to compute the representative list of a RSDG, given the fact profile
def genRL(gt,knob_samples, threshold, knobs):
    #gT is a dictionary where entry is the config and value is hte cost
    #profile_configs is the structured configuration

    # segmentation level
    seglvl = 0
    # initial error rate set to 100%
    error = 1.0

    while error>=threshold:
        if seglvl >= 1:
            break
        seglvl += 1
        partitions = partition(seglvl,knob_samples)
        observed_profile = retrieve(partitions, gt, knobs)
        rsdg = populate(observed_profile)
        error = compare(rsdg,gt)
    return

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
    return partitions

# given a partition list, retrieve the data points in ground truth
# return a profile by observation
def retrieve(partitions, gt, knobs):
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
        costVal = gt.getCost(configuration)
        print costVal
        observed_profile.addEntry(configuration,costVal)
    return observed_profile

# given an observed profile, generate the continuous problem and populate the rsdg
def populate(observed):
    # write the observation to an observed file
    observed.printProfile("observed.csv")
    populateRSDG("observed.csv","profile.csv",True,"quad",False)
    return 0

def compare(rsdg,groundTruth):
    return 1.0