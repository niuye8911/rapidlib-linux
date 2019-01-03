import sys

from Classes import *
from qos_checker import *

appName = ""
output = ""

# binaries
# update the path below when new apps are added
bin_swaptions = "swaptions"
bin_bodytrack = "bodytrack"
bin_ferret = "ferret"

# input path
body_input = "/home/liuliu/Research/input/parsec-3.0/pkgs/apps/bodytrack" \
             "/inputs/sequenceB_4"
swap_output = "/home/liuliu/Research/parsec3.0-rapid-source/parsec-3.0/pkgs" \
              "/apps/swaptions/src"
ferret_input = "/home/liuliu/Research/parsec3.0-rapid-source/parsec-3.0/pkgs" \
               "/apps/ferret/run/"


# Run the application with developer-provided methods
# The expected behavior of this application should be writing Cost and QoS
# metric to corresponding files
def run(appName, config_table):
    config_table = config_table.configurations
    if not os.path.exists("./training_outputs"):
        os.system("mkdir ./training_outputs")
    costFact = open("./outputs/" + appName + "-cost" + ".fact", 'w')
    mvFact = open("./outputs/" + appName + "-mv" + ".fact", 'w')
    if appName == "bodytrack":
        # for bodytrack
        particle = 0
        layer = 0
        # generate the ground truth
        print
        "GENERATING GROUND TRUTH for BODYTRACK"
        command = [bin_bodytrack,
                   body_input,
                   "4", "4",
                   str(4000),
                   str(5),
                   '4']
        subprocess.call(command)
        gt_path = "./training_outputs/grountTruth.txt"
        command = ["mv", body_input + "/poses.txt", gt_path]
        subprocess.call(command)
        # generate the facts
        for configuration in config_table:
            configs = configuration.retrieve_configs()
            for config in configs:
                name = config.knob.set_name
                if name == "particle":
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
            costFact.write('particle,{0},layer,{1},{2}\n'.format(int(particle),
                                                                 int(layer),
                                                                 elapsedTime))
            newfileloc = "./training_outputs/output_" + str(
                int(particle)) + "_" + str(int(layer)) + ".txt"
            command = ["mv", body_input + "/poses.txt", newfileloc]
            subprocess.call(command)
            # generate mv fact
            mvFact.write(
                'particle,{0},layer,{1},'.format(int(particle), int(layer)))
            checkBodytrack(gt_path, newfileloc, False, mvFact)
            mvFact.write("\n")
        costFact.close()
        mvFact.close()

    elif appName == "swaptions":
        # for swaptions
        num = 0.0
        # generate the ground truth
        print
        "GENERATING GROUND TRUTH for SWAPTIONS"
        command = [bin_swaptions,
                   # make sure the bin_swaptions is updated when doing the
                   # walk-through
                   "-ns",
                   "10",
                   "-sm",
                   str(1000000)
                   ]
        # in case subprocess might not work
        # subprocess.call(command)
        os.system(" ".join(command))
        gt_path = "./training_outputs/grountTruth.txt"
        command = ["mv", "./output.txt", gt_path]
        subprocess.call(command)

        # generate the facts
        for configuration in config_table:
            configs = configuration.retrieve_configs()  # extract the
            # configurations
            for config in configs:
                name = config.knob.set_name
                if name == "num":
                    num = config.val  # retrieve the setting for each knob

            # assembly the command
            command = [bin_swaptions,
                       "-ns",
                       "10",
                       "-sm",
                       str(num)
                       ]

            # measure the execution time for the run
            time1 = time.time()
            # subprocess.call(command)
            os.system(" ".join(command))
            time2 = time.time()
            elapsedTime = (
                                  time2 - time1) * 1000 / 10  # divided by 10
            # because in each run, 10 jobs(swaption) are done
            # write the cost to file
            costFact.write('num,{0},{1}\n'.format(int(num), elapsedTime))
            # mv the generated output to another location
            newfileloc = "./training_outputs/output_"
            command = ["mv", "./output.txt", newfileloc]
            subprocess.call(command)
            # write the mv to file
            mvFact.write('num,{0},'.format(int(num)))
            checkSwaption(gt_path, newfileloc, False, mvFact)
            mvFact.write("\n")

        costFact.close()
        mvFact.close()

    elif appName == "ferret":
        # for bodytrack
        hash = 0.0
        probe = 0.0
        itr = 0.0
        # generate the ground truth
        print
        "GENERATING GROUND TRUTH for Ferret"
        command = [bin_ferret,
                   ferret_input + "corelnative",
                   "lsh",
                   ferret_input + "queries",
                   "50",
                   "20",
                   "1",
                   "output.txt",
                   "-l",
                   str(8),
                   "-t",
                   str(20),
                   "-itr",
                   str(25)
                   ]
        subprocess.call(command)
        print
        "Done: GENERATING GROUND TRUTH for Ferret"
        gt_path = "./training_outputs/grountTruth.txt"
        command = ["mv", "./output.txt", gt_path]
        subprocess.call(command)
        # generate the facts
        for configuration in config_table:
            configs = configuration.retrieve_configs()
            for config in configs:
                name = config.knob.set_name
                if name == "hash":
                    hash = config.val
                elif name == "iteration":
                    itr = config.val
                else:
                    probe = config.val
            command2 = [bin_ferret,
                        ferret_input + "corelnative",
                        "lsh",
                        ferret_input + "queries",
                        "50",
                        "20",
                        "1",
                        "output.txt",
                        "-l",
                        str(int(hash)),
                        "-t",
                        str(int(probe)),
                        "-itr",
                        str(int(itr))
                        ]
            time1 = time.time()
            subprocess.call(command2)
            time2 = time.time()
            elapsedTime = (time2 - time1) * 1000 / 20
            costFact.write(
                'hash,{0},probe,{1},iteration,{2},{3}\n'.format(int(hash),
                                                                int(probe),
                                                                int(itr),
                                                                elapsedTime))
            newfileloc = "./training_outputs/output_" + str(
                int(hash)) + "_" + str(int(probe)) + "_" + str(
                int(itr)) + ".txt"
            command = ["mv", "./output.txt", newfileloc]
            subprocess.call(command)
            # generate mv fact
            mvFact.write('hash,{0},probe,{1},iteration,{2},'.format(int(hash),
                                                                    int(probe),
                                                                    int(itr)))
            checkFerret(gt_path, newfileloc, False, mvFact)
            mvFact.write("\n")
        costFact.close()
        mvFact.close()


def main(argv):
    global appName, output
    args = argv
    if (len(args) != 2 or args[0] != "-a"):
        print
        "usage: python performance.py -a [appName]"
        exit(0)
    appName = argv[1]
    output = open("performance_" + appName, 'w')
    run()
    output.close()


if __name__ == "__main__":
    main(sys.argv[1:])
