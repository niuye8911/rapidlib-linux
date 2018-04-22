from performance import *
def genFact(appname,config_table):
    path = "outputs/"+appname+".fact"
    run(appname,config_table)
    return path