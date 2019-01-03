from piecewiseProb import *
from quadProb import *
from stage_1.training import *


# contains functions to compute the representative list of a RSDG, given the
# fact profile
def constructRSDG(gt, knob_samples, threshold, knobs, PRINT, model, seglvl=0):
    # gT is a dictionary where entry is the config and value is hte cost
    # profile_configs is the structured configuration
    # segmentation level

    # initial error rate set to 100%
    error = 1.0
    maxT = 3
    if model == "quad":
        maxT = 3
    if seglvl == 0:
        while error >= threshold:
            if seglvl >= maxT:
                print
                "Reached Highest Segmentation Granularity"
                break
            seglvl += 1
            partitions = partition(seglvl, knob_samples)
            observed_profile = retrieve(partitions, gt, knobs)
            costrsdg, mvrsdgs, costpath, mvpaths = populate(observed_profile,
                                                            partitions, model)
            error = compare(costrsdg, gt, False, model)
    else:
        partitions = partition(seglvl, knob_samples)
        observed_profile = retrieve(partitions, gt, knobs)
        costrsdg, mvrsdgs, costpath, mvpaths = populate(observed_profile,
                                                        partitions, model)
        error = compare(costrsdg, gt, False, model)
    if PRINT:
        compare(costrsdg, gt, True, model)
        print
        "Granulatiry = " + str(seglvl)
    return costrsdg, mvrsdgs, costpath, mvpaths, seglvl


# given a partion level, return a list of configurations
def partition(seglvl, knob_samples):
    partitions = {}
    # seglvl indicate the number of partition lvl on each knob
    for knob in knob_samples:
        val_range = knob_samples[knob]
        length = len(val_range)
        partitions[knob] = []
        max = length - 1
        min = 0
        # determine the step size
        num_of_partitions = 2 ** (seglvl - 1)
        step = length / num_of_partitions - 1
        if step < 1:
            step = 1
        for i in range(min, max + 1, step):
            partitions[knob].append(val_range[i])
        # extend the last one to the end
        length = len(partitions[knob])
        partitions[knob][length - 1] = val_range[max]
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
            single_set.append(Config(knobs.getKnob(knob), sample))
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
        mvvals = gt.getMV(configuration)
        observed_profile.addCostEntry(configuration, costval)
        observed_profile.addMVEntry(configuration, mvvals)
    return observed_profile


# given an observed profile, generate the continuous problem and populate the
# rsdg
def populate(observed, partitions, model):
    if model == "piecewise":
        return populatePieceWiseRSDG(observed, partitions)
    elif model == "quad":
        return populateQuadRSDG(observed, True)
    elif model == "linear":
        return populateQuadRSDG(observed, False)


def compare(rsdg, groundTruth, PRINT, model):
    if model == "piecewise":
        return modelValid(rsdg, groundTruth, PRINT)
    elif model == "quad":
        return compareQuadRSDG(groundTruth, rsdg, True, PRINT)
    elif model == "linear":
        return compareQuadRSDG(groundTruth, rsdg, False, PRINT)
