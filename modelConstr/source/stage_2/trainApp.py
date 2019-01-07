import os

from Classes import AppMethods


def recoverTimeRecord(appname, units):
    time_record = {}
    with open("./outputs/" + appname + "-cost.fact") as costfile:
        for line in costfile:
            col = line.split()
            unit_cost = col[-1]
            configs = []
            config_part = col[0:-1]
            for i in range(0, len(config_part) - 1, 2):
                name = config_part[i]
                val = config_part[i + 1]
                configs.append(name + "-" + val)
            config = "-".join(sorted(configs))
            time_record[config] = float(unit_cost) * units
    return time_record


def genFact(appname, config_table, appMethods, withQoS, withSys, withPerf,
            numOfFixedEnv):
    cost_path = "outputs/" + appname + "-cost" + ".fact"
    mv_path = "outputs/" + appname + "-mv" + ".fact" if withQoS else ''
    sys_path = "outputs/" + appname + "-sys" + ".csv" if withSys else ''
    perf_path = "outputs/" + appname + "-perf" + ".csv" if withPerf else ''
    # if the training has been done, just exit

    if os.path.exists(cost_path):
        # construct the time_record
        print("already trained")
        time_record = recoverTimeRecord(appname, appMethods.training_units)
        return cost_path, mv_path, time_record
    # run(appname,config_table)
    if withQoS:
        appMethods.runGT()
    training_time_record = appMethods.train(
        config_table, numOfFixedEnv, cost_path, mv_path, sys_path, perf_path)
    return cost_path, mv_path, training_time_record


def genFactWithRSDG(appname, config_table, cost_rsdg, mv_rsdgs, appMethod,
                    preferences):
    print
    cost_rsdg.coeffTable
    # generate the fact file using existing rsdg
    cost_path = "outputs/" + appname + "-cost-gen" + ".fact"
    mv_path = "outputs/" + appname + "-mv-gen" + ".fact"
    costFile = open(cost_path, 'w')
    mvFile = open(mv_path, 'w')
    configurations = config_table.configurations
    for configuration in configurations:
        cost = cost_rsdg.calCost(configuration)
        AppMethods.writeConfigMeasurementToFile(costFile, configuration, cost)
        mvs = map(lambda x: x.calCost(configuration), mv_rsdgs)
        combined_mv = appMethod.computeQoSWeight(preferences, mvs)
        AppMethods.writeConfigMeasurementToFile(mvFile, configuration,
                                                combined_mv)
    return cost_path, mv_path
