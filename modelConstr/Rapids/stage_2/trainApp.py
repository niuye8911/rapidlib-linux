import imp

def genFact(appInfo, config_table, bb_profile, numOfFixedEnv):
    ''' return the a table containing the training time '''
    module = imp.load_source("", appInfo.METHODS_PATH)
    appMethods = module.appMethods(appInfo.APP_NAME, appInfo.OBJ_PATH)
    # first get the GT ready if withQoS
    if appInfo.TRAINING_CFG['withQoS']:
            appMethods.runGT()
    training_time_record = appMethods.train(config_table,bb_profile, numOfFixedEnv,
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
