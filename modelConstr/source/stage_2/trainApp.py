from performance import *
def genFact(appname,config_table,appMethods):
    cost_path = "outputs/"+appname+"-cost"+".fact"
    mv_path = "outputs/"+appname+"-mv"+".fact"
    #run(appname,config_table)
    appMethods.runGT()
    appMethods.train(config_table,cost_path,mv_path,False,True)
    return cost_path,mv_path

def genSysUsage(appname,config_table,appMethods):
    sys_path = "outputs/"+appname+"-sys"+".fact"
    appMethods.train(config_table,cost_path,mv_path,True)
    return sys_path
