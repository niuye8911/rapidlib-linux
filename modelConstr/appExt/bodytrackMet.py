"""
This is an example file for prepraing Bodytrack for RAPID(C)
"""

from Rapids_Classes.AppMethods import AppMethods  # import the parent class and other classes from the
import os
import numpy as np


class appMethods(AppMethods):
    input_path = "/home/liuliu/Research/mara_bench/parsec_rapid/pkgs/apps" \
                 "/bodytrack/run/sequenceB_261/"

    def __init__(self, name, obj_path):
        """ Initialization with app name
        :param name:
        """
        AppMethods.__init__(self, name, obj_path)
        self.training_units = 30
        self.fullrun_units = 261
        self.max_cost = 293
        self.min_cost = 25
        self.min_mv = 65.69
        self.max_mv = 100
        self.gt_path = "./training_outputs/body-gt.txt"

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

        self.moveFile(
            self.input_path + "poses.txt", "./training_outputs/output_" +
            str(layer) + "_" + str(particle) + ".txt")

    def afterGTRun(self):
        if not os.path.exists(self.gt_path):
            output_path = self.input_path + "poses.txt"
            self.moveFile(output_path, self.gt_path)

    def getFullRunCommand(self, budget, xml='', OFFLINE=False,UNIT=-1):
        xml_path = xml if xml != '' else "./outputs/" + self.appName + "-default.xml"
        if UNIT==-1:
            unit = 10000 # arbiturary large, then no reconfig
        else:
            unit = max(1,int(self.fullrun_units / UNIT))
        cmd = [
            self.obj_path, self.input_path, "4", '261', '4000', '5', '4', '1',
            "-rsdg", "-cont", "-b",
            str(budget), "-u", str(unit), "-xml", xml_path
        ]
        if OFFLINE:
            cmd = cmd + ['-offline']
        return cmd

    # helper function to assembly the command
    def getCommand(self, configs=None, qosRun=False, fullRun=True):
        if qosRun and os.path.exists(self.gt_path):
            return ['ls']
        particle = 4000
        layer = 5
        if not configs == None:
            for config in configs:
                name = config.knob.set_name
                if name == "particle":
                    particle = config.val  # retrieve the setting for each knob
                elif name == "layer":
                    layer = config.val  # retrieve the setting for each knob
        if qosRun or fullRun:
            units = self.fullrun_units
        else:
            units = self.training_units
        return [
            self.obj_path, self.input_path, "4",
            str(units),
            str(particle),
            str(layer), '4', '1'
        ]

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
        totDistortion = []
        for i in range(0, len(truth_results[0])):
            # truth_results[i] is a vector, compute the vector distortion
            if i >= 3 and i <= 5:  #exclude the three large numbers
                continue
            distortion = 0.0
            # get the vector for the truth
            vector_gt = list(map(lambda x: x[i], truth_results))
            vector_mission = list(map(lambda x: x[i], mission_results))
            if not len(vector_gt) == len(vector_mission):
                print("not finished")
                return 0.0
            mag = np.linalg.norm(vector_gt)
            dist = [
                abs((float(i) - float(j)) / float(i))
                for i, j in zip(vector_gt, vector_mission)
            ]
            dist = np.mean(dist) / mag
            totDistortion.append(dist)
        return 5-np.mean(totDistortion)

    # helper function to evaluate the QoS
    def getQoS_DEPRECATED(self):
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
                try:
                    curmission = float(mission_results[i][j])
                except IndexError:
                    print('cannot find')
                    curmission = 0.0
                val = abs((curtrue - curmission) / curtrue)
                if val > 1:
                    val = 1
                distortion += val
            distortion /= len(truth_results[i])
            totDistortion += distortion
        return (1.0 - (totDistortion / len(truth_results))) * 100.0
