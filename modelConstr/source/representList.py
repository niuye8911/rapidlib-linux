from tranning import crossproduct
# contains functions to compute the representative list of a RSDG, given the fact profile
def genRL(groundTruth,knob_samples, threshold):
    #gT is a dictionary where entry is the config and value is hte cost
    #profile_configs is the structured configuration

    # segmentation level
    seglvl = 0
    # initial error rate set to 100%
    error = 1.0

    while error>=threshold:
        if seglvl > 4:
            break
        seglvl += 1
        partitions = partition(seglvl,knob_samples)
        observed = retrieve(partitions, groundTruth)
        rsdg = populate(observed)
        error = compare(rsdg,groundTruth)
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
def retrieve(partitions, gt):
    return 0

def populate(observed):
    return 0

def compare(rsdg,groundTruth):
    return 1.0