import os
from Classes import AppMethods

def genFact(appname, config_table, appMethods, withQoS, withSys, withPerf,
            numOfFixedEnv):
    cost_path = "outputs/" + appname + "-cost" + ".fact"
    mv_path = "outputs/" + appname + "-mv" + ".fact" if withQoS else ''
    sys_path = "outputs/" + appname + "-sys" + ".csv" if withSys else ''
    perf_path = "outputs/" + appname + "-perf" + ".csv" if withPerf else ''
    # if the training has been done, just exit

    if os.path.exists(cost_path):
        return cost_path, mv_path
    # run(appname,config_table)
    if withQoS:
        appMethods.runGT()
    appMethods.train(config_table, numOfFixedEnv, cost_path, mv_path,
                     sys_path, perf_path)
    return cost_path, mv_path

def genFactWithRSDG(appname, config_table, cost_rsdg, mv_rsdgs, appMethod, preferences):
    print cost_rsdg.coeffTable
    # generate the fact file using existing rsdg
    cost_path = "outputs/" + appname + "-cost-gen" + ".fact"
    mv_path = "outputs/" + appname + "-mv-gen" + ".fact"
    costFile = open(cost_path,'w')
    mvFile = open(mv_path,'w')
    configurations = config_table.configurations
    for configuration in configurations:
        cost = cost_rsdg.calCost(configuration)
        AppMethods.writeConfigMeasurementToFile(costFile,configuration,cost)
        mvs = map(lambda x: x.calCost(configuration), mv_rsdgs)
        combined_mv = appMethod.computeQoSWeight(preferences, mvs)
        AppMethods.writeConfigMeasurementToFile(mvFile, configuration, combined_mv)
    return cost_path, mv_path
