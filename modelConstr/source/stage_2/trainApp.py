from performance import *
def genFact(appname,config_table):
    cost_path = "outputs/"+appname+"-cost"+".fact"
    mv_path = "outputs/"+appname+"-mv"+".fact"
    run(appname,config_table)
    return cost_path,mv_path