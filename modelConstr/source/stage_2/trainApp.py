from performance import *
def genFact(appname,config_table,appMethods):
    cost_path = "outputs/"+appname+"-cost"+".fact"
    mv_path = "outputs/"+appname+"-mv"+".fact"
    #run(appname,config_table)
    appMethods.runGT()
    appMethods.train(config_table,cost_path,mv_path)
    return cost_path,mv_path
