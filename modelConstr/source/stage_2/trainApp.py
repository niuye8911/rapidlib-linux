from performance import *
def genFact(appname,config_table):
    path = "outputs/"+appname+"-cost"+".fact"
    run(appname,config_table)
    return path