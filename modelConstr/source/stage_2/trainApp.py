from performance import *


def genFact(appname, config_table, appMethods, withQoS, withSys):
    cost_path = "outputs/"+appname+"-cost"+".fact"
    mv_path = "outputs/"+appname+"-mv"+".fact"
    #run(appname,config_table)
    if withQoS:
        appMethods.runGT()
    appMethods.train(config_table, cost_path, mv_path, withQoS, withSys)
    return cost_path,mv_path
