from LP_Util.lp_util import *
from contigous import *
from stage_4.constructRSDG import *
from util import *


def genContRS(gt, targetMean, KDG=True):
    '''generate the representative set for continuous apps
    '''
    print("generating RS")
    observed_profile = Profile()
    configurations = gt.configurations
    curMean = 1.1
    # select the most expensive and the cheapest
    min_cost = 9e9
    max_cost = -9e9
    for configuration in configurations:
        cur_cost = gt.getCost(configuration)
        if cur_cost > max_cost:
            top_config = configuration
            max_cost = cur_cost
        if cur_cost < min_cost:
            bottom_config = configuration
            min_cost = cur_cost
    observed_profile.addEntry(top_config, max_cost, gt.getMV(top_config))
    observed_profile.addEntry(bottom_config, min_cost, gt.getMV(bottom_config))

    # iteratively add configs until the targetMean is fulfilled
    while curMean > targetMean:
        selected = None
        curMinErr = 1.1
        for config in configurations:
            if observed_profile.hasEntry(config):
                continue
            observed_profile.addEntry(config, gt.getCost(config),
                                      gt.getMV(config))
            # calculate the error
            partitions = Profile.getPartitions(observed_profile.configurations)
            costrsdg, mvrsdgs, costpath, mvpaths = populate(
                observed_profile, partitions, "piecewise", KDG)
            error = compare(costrsdg, gt, True, "piecewise")
            if error <= curMinErr:
                selected = config
                curMinErr = error
            observed_profile.removeConfig(config)
        observed_profile.addEntry(selected, gt.getCost(selected),
                                  gt.getMV(selected))
        curMean = curMinErr
    return observed_profile.configurations, curMean


def getConfigurationsFromFile(validate_rs_path, knobs):
    configurations = []
    with open(validate_rs_path, 'r') as rs:
        for line in rs:
            col = line.split(',')
            knob_name = ""
            knob_val = 0.0
            configuration = Configuration()
            if len(col) == 1:
                # last line
                continue
            for i in range(len(col)):
                col[i] = col[i].split()[0]
                if col[i].isdigit():
                    knob_val = int(col[i])
                    configuration.addConfig(
                        [Config(knobs.getKnob(knob_name), knob_val)])
                else:
                    knob_name = col[i]
            configurations.append(configuration)
    return configurations


def validateRS(gt, rs_configurations):
    observed_profile = Profile()
    # generate the observed profile
    for configuration in rs_configurations:
        observed_profile.addEntry(configuration, gt.getCost(configuration),
                                  gt.getMV(configuration))
    partitions = Profile.getPartitions(observed_profile.configurations)
    costrsdg, mvrsdgs, costpath, mvpaths = populate(observed_profile,
                                                    partitions, "piecewise")
    error = compare(costrsdg, gt, True, "piecewise")
    print
    "Validation: " + str(error)


# fact : fact file mode : whether is to get a set of a list
def genRS(fact, set, targetMax, targetMean):
    global configs, service_levels
    represented_set = []
    selected = {}  # selected configurations id in RS
    curConfigs = []  # selected configurations in RS
    # get the configs from the file
    configs, service_levels = generateConfigsFromTraining(fact)
    totalNumOfConfigs = len(configs)

    # add the top and last config
    curConfigs.append(configs[0])
    curConfigs.append(configs[totalNumOfConfigs - 1])

    represented_set.append(configs[0])
    represented_set.append(configs[totalNumOfConfigs - 1])

    selected[0] = True
    selected[totalNumOfConfigs - 1] = True

    # iterate through all constraints
    curMeanErr = 10.0
    curMaxErr = 10.0
    smallest = -1
    while len(represented_set) <= totalNumOfConfigs:  # target mean err
        smallest = -2
        biggestinsmallest = -2
        maxErrTmp = 10.0
        for i in range(1, totalNumOfConfigs - 1):
            if (selected.has_key(i)): continue  # if already in the list
            # add the new config to the RS
            curConfigs.append(configs[i])
            # generate the optimization problem
            genProblem(service_levels, curConfigs)
            # fetch the resulting rsdg
            rsdg = solveAndPopulate(service_levels, False, False)
            [meanErr, maxErr, maxId] = checkRate(rsdg, fact)
            if (meanErr <= maxErrTmp):
                maxErrTmp = meanErr
                curMeanErr = meanErr
                curMaxErr = maxErr
                smallest = i
                biggestinsmallest = maxId
            # pop out the newly added config
            curConfigs.pop()
        # add the one config that is the smallest into the
        selected[smallest] = True
        print
        "Mean:" + str(curMeanErr) + "\tMax:" + str(
            curMaxErr) + "\tselected:" + str(smallest) + "/" + str(
            biggestinsmallest)
        print
        "maxConfig:" + str(maxId)
        represented_set.append(configs[smallest])
        curConfigs.append(configs[smallest])
        # determine whether to stop the iteration
        if (set):
            if not (smallest == -2 and
                    (curMeanErr >= targetMean or curMaxErr >= targetMax)):
                break
        else:
            continue

    # generate the final problem
    genProblem(service_levels, curConfigs)
    rsdg = solveAndPopulate(service_levels, True, False)
    checkRate(rsdg, fact)

    # write result to a file
    resFile = open("./outputs/RS", 'w')
    for eachConfig in represented_set:
        resFile.write(eachConfig.print_yourself())
        resFile.write("\n")
    return represented_set


# populate a fully blown RSDG with observed measurement
def populateRSDG(observedFile, factFile, cont, model, remote):
    if cont == True:
        quad = True
        if not (model == "" or model == "quad"):
            quad = False
        paras = genContProblem(factFile, quad)
        os.system("gurobi_cl LogFile=gurobi.log OutputFlag=0 "
                  "ResultFile=outputs/max.sol outputs/contproblem.lp")
        print
        paras
        getContRSDGandCheckRate(paras, factFile, quad)
        return

    global configs, service_levels
    # setup the configuration
    configs, service_levels = generateConfigsFromTraining(factFile)
    observed_configs, dummy = generateConfigsFromTraining(observedFile)
    genProblem(service_levels, observed_configs)
    rsdg = solveAndPopulate(service_levels, True, remote)
    [meanErr, maxErr, maxId] = checkRate(rsdg, factFile)
    print
    "Mean:" + str(meanErr) + "\tMax:" + str(maxErr)
    print
    "maxConfig:" + str(maxId)
