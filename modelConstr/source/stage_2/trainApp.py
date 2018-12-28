import os


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
