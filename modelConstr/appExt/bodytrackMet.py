"""
This is an example file for prepraing Bodytrack for RAPID(C)
"""

from Classes import *  # import the parent class and other classes from the


# file Classes.py


class appMethods(AppMethods):
    input_path = "/home/liuliu/Research/mara_bench/parsec-3.0/pkgs/apps" \
                 "/bodytrack/run/sequenceB_261/"

    def __init__(self, name, obj_path):
        """ Initialization with app name
        :param name:
        """
        AppMethods.__init__(self, name, obj_path)
        self.training_units = 20
        self.fullrun_units = 241
        self.max_cost = 251
        self.min_cost = 100
        self.gt_path = "./training_outputs/grountTruth.txt"

    def cleanUpAfterEachRun(self, configs=None):
        # backup the generated output to another location
        particle = 4000
        layer = 5
        if configs is not None:
            for config in configs:
                name = config.knob.set_name
                if name == "particle":
                    particle = config.val  # retrieve the setting for each knob
                elif name == "layer":
                    layer = config.val  # retrieve the setting for each knob

        self.moveFile(self.input_path + "poses.txt",
                      "./training_outputs/output_" + str(layer) + "_" + str(
                          particle) + ".txt")

    def afterGTRun(self):
        self.gt_path = "./training_outputs/grountTruth.txt"
        output_path = self.input_path + "poses.txt"
        self.moveFile(output_path, self.gt_path)

    def getFullRunCommand(self, budget):
        return [self.obj_path,
                self.input_path,
                "4", '241',
                '4000',
                '5',
                '4',
                '1',
                "-rsdg", "-cont",
                "-b", str(budget),
                "-xml", "./outputs/" + self.appName + "-default.xml",
                "-u", '24']

    # helper function to assembly the command
    def getCommand(self, configs=None, qosRun=False):
        particle = 4000
        layer = 5
        if not configs == None:
            for config in configs:
                name = config.knob.set_name
                if name == "particle":
                    particle = config.val  # retrieve the setting for each knob
                elif name == "layer":
                    layer = config.val  # retrieve the setting for each knob
        if qosRun:
            units = self.training_units
        else:
            units = self.fullrun_units
        return [self.obj_path,
                self.input_path,
                "4", str(units),
                str(particle),
                str(layer),
                '4',
                '1']

    # helper function to evaluate the QoS
    def getQoS(self):
        """
        In our example, after each run of the application, this function will
        be called to compare the current output
        with the groundtruth output.

        Two files both contains multiple rows where each row represents the
        calculated mean price for a swaption. We
        extract the mean price and calculate the distortion
        :return: a double value describing the QoS ( 0.0 ~ 100.0 )
        """
        gt_output = open(self.gt_path, "r")
        mission_output = open(self.input_path + "poses.txt", "r")
        truth_results = []
        mission_results = []
        totalRound = 0
        for line in gt_output:
            round_res = line.split()
            truth_results.append(round_res)
        for line in mission_output:
            round_res = line.split()
            mission_results.append(round_res)
        totDistortion = 0.0

        for i in range(0, len(truth_results)):
            # truth_results[i] is a vector, compute the vector distortion
            distortion = 0.0
            for j in range(0, len(truth_results[i])):
                if (truth_results[i][j] == "\n"):
                    continue
                curtrue = float(truth_results[i][j])
                curmission = float(mission_results[i][j])
                val = abs((curtrue - curmission) / curtrue)
                if val > 1:
                    val = 1
                distortion += val
            distortion /= len(truth_results[i])
            print
            "DISTORTION = " + str(distortion)
            totDistortion += distortion
        return (1.0 - (totDistortion / len(truth_results))) * 100.0
