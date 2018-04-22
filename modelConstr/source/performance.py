import time
import sys
import getopt
import numpy
import subprocess
from Classes import *
import os

appName = ""
output = ""

# binaries
bin_swaptions = "swaptions"
bin_bodytrack = "bodytrack"
bin_ferret = "ferret"

# knobs
body_input = "/home/liuliu/Research/input/parsec-3.0/pkgs/apps/bodytrack/inputs/sequenceB_4"

knob_swaptions = [100000, 200000, 300000, 400000, 500000, 600000, 700000, 800000, 900000, 1000000]

knob_ferret_itr = numpy.linspace(1, 25, num=25)
knob_ferret_hash = numpy.linspace(2, 8, num=4)
knob_ferret_probe = numpy.linspace(2, 20, num=10)


# iterative functions
def run(appName,config_table):
    config_table = config_table.configurations
    if not os.path.exists("./training_outputs"):
        os.system("mkdir ./training_outputs")
    costFact = open("./outputs/"+appName+".fact",'w')
    if appName == "bodytrack":
        # for bodytrack
        costFact.write('{:<10} {:<10} {:<20}'.format("Particles", "Annealing", "elapsedTime(ms)") + '\n')
        particle = 0
        layer = 0
        for configuration in config_table:
            configs = configuration.retrieve_configs()
            for config in configs:
                name = config.knob.set_name
                if name== "particle":
                    particle = config.val
                else:
                    layer = config.val
            command = [bin_bodytrack,
                           body_input,
                           "4", "4",
                           str(int(particle)),
                           str(int(layer)),
                           '4']
            time1 = time.time()
            subprocess.call(command)
            time2 = time.time()
            elapsedTime = (time2 - time1) * 1000 / 4
            costFact.write('{:<10d} {:<10d} {:<20f}'.format(int(particle), int(layer),elapsedTime) + '\n')
            newfileloc = "./training_outputs/output_" + str(int(particle)) + "_" + str(int(layer)) + ".txt"
            command = ["mv", body_input+"/poses.txt", newfileloc]
            subprocess.call(command)
        costFact.close()

    elif appName == "swaptions":
        output.write('{:<10} {:<20}'.format("NumIter", "elapsedTime(ms)") + '\n')
        global bin_swaptions
        for i in range(0, len(knob_swaptions)):  # run the application for each configuratino
            command = [bin_swaptions,
                       "-ns",
                       "10",
                       "-sm",
                       str(knob_swaptions[i])
                       ]
            time1 = time.time()
            subprocess.call(command)
            time2 = time.time()
            elapsedTime = (time2 - time1) * 1000 / 10  # milli second per round(swaption)
            output.write('{:<10d} {:<20f}'.format(knob_swaptions[i], elapsedTime) + '\n')
            # cp the result file to somewhere else
            newfileloc = "output_" + str(knob_swaptions[i]) + ".txt"
            command = ["mv", "output.txt", newfileloc]
            subprocess.call(command)

    elif appName == "ferret":
        output.write('{:<10} {:<20} {:<10} {:<20}'.format("NumHash", "NumProbe", "NumItr", "elapsedTime(ms)") + '\n')
        global bin_ferret, knob_ferret_probe, knob_ferret_itr, knob_ferret_hash
        for i in range(0, len(knob_ferret_hash)):  # run the application for each configuratino
            for j in range(0, len(knob_ferret_probe)):
                for k in range(0, len(knob_ferret_itr)):
                    command2 = [bin_ferret,
                                "corel",
                                "lsh",
                                "queries_offline_small",
                                "50",
                                "20",
                                "1",
                                "output.txt",
                                "-l",
                                str(int(knob_ferret_hash[i])),
                                "-t",
                                str(int(knob_ferret_probe[j])),
                                "-itr",
                                str(int(knob_ferret_itr[k]))
                                ]
                    time1 = time.time()
                    subprocess.call(command2)
                    time2 = time.time()
                    elapsedTime = (time2 - time1) * 1000 / 10  # milli second per round(swaption)
                    output.write('{:<10} {:<20} {:<10} {:<20}'.format(knob_ferret_hash[i], knob_ferret_probe[j],
                                                                      knob_ferret_itr[k], "elapsedTime(ms)") + '\n')
                    # cp the result file to somewhere else
                    newfileloc = "output_" + str(int(knob_ferret_hash[i])) + "_" + str(
                        int(knob_ferret_probe[j])) + "_" + str(
                        int(knob_ferret_itr[k])) + ".txt"
                    command = ["mv", "output.txt", newfileloc]
                    subprocess.call(command)


def main(argv):
    global appName, output
    args = argv
    if (len(args) != 2 or args[0] != "-a"):
        print "usage: python performance.py -a [appName]"
        exit(0)
    appName = argv[1]
    output = open("performance_" + appName, 'w')
    run()
    output.close()


if __name__ == "__main__":
    main(sys.argv[1:])
