import imp

from Classes import AppMethods


def recoverTimeRecord(appInfo, units):
    ''' estimate the total training time from a trained cost profile '''
    time_record = {}
    with open(appInfo.FILE_PATHS['COST_FILE_PATH'], 'r') as costfile:
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


def genFact(appInfo, config_table, numOfFixedEnv):
    ''' return the a table containing the training time '''
    module = imp.load_source("", appInfo.METHODS_PATH)
    appMethods = module.appMethods(appInfo.APP_NAME, appInfo.OBJ_PATH)
    # if the training has been done, use the trained data
    if appInfo.isTrained():
        # construct the time_record
        time_record = recoverTimeRecord(appInfo, appMethods.training_units)
        return time_record
    if appInfo.TRAINING_CFG['withQoS']:
        appMethods.runGT()
    training_time_record = appMethods.train(config_table, numOfFixedEnv,
                                            appInfo)
    return training_time_record


def genFactWithRSDG(appname, config_table, cost_rsdg, mv_rsdgs, appMethod,
                    preferences):
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
