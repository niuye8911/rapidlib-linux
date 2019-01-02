import os
import json

def run(preferences):
    # generate the xml
    cmd = [ 'python',
            config['rapidScript'],
            '--cfg',
            './ferret_run.config',
            "--model",
            "piecewise",
            "-m",
            "finalize",
            ]
    os.system(" ".join(cmd))
    # move the xml
    mv_cmd = ['mv',
            '/home/liuliu/Research/rapidlib-linux/modelConstr/source/outputs/ferret.xml',
             './xmls/ferret'+"_"+str(preferences[0])+"_"+str(preferences[1])+".xml"]
    os.system(" ".join(mv_cmd))


with open('./ferret_run.config','r') as config_json:
    config = json.load(config_json)

for preferences in range (1,11):
    # relavance from 1 to 10
    config['preferences'][0] = float(preferences)
    configfile = open('./ferret_run.config','w')
    json.dump(config,configfile,indent=2, sort_keys=True)
    configfile.close()
    run(config['preferences'])
