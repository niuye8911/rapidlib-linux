"""
This is an example file for prepraing Bodytrack for RAPID(C)
"""

import math

from Classes import *  # import the parent class and other classes from the


# file Classes.py


class appMethods(AppMethods):
    run_path = "/home/liuliu/Research/mara_bench/rrt-simulator/"

    def cleanUpAfterEachRun(self, configs=None):
        obstacleDistance = 25
        trials = 100
        goalBias = 10
        goalTolerance = 0
        stepSize = 3
        if configs is not None:
            for config in configs:
                name = config.knob.set_name
                if name == "obstacleDistance":
                    obstacleDistance = 6 - config.val  # retrieve the setting
                    # for each knob
                elif name == "trials":
                    trials = config.val  # retrieve the setting for each knob
                elif name == "goalBias":
                    goalBias = 60 - config.val  # retrieve the setting for
                    # each knob
                elif name == "goalTolerance":
                    goalTolerance = 11 - config.val  # retrieve the setting
                    # for each knob
                elif name == "stepSize":
                    stepSize = config.val  # retrieve the setting for each knob

        self.moveFile("./rrtout.txt",
                      "./training_outputs/output_" + str(obstacleDistance) + "_"
                      + str(trials) + "_"
                      + str(goalBias) + "_"
                      + str(goalTolerance) + "_"
                      + str(stepSize) +
                      ".txt")

    def afterGTRun(self):
        pass

    # helper function to assembly the command
    def getCommand(self, configs=None):
        obstacleDistance = 25
        trials = 100
        goalBias = 10
        goalTolerance = 0
        stepSize = 3
        if configs is not None:
            for config in configs:
                name = config.knob.set_name
                if name == "obstacleDistance":
                    obstacleDistance = 6 - config.val  # retrieve the setting
                    # for each knob
                elif name == "trials":
                    trials = config.val  # retrieve the setting for each knob
                elif name == "goalBias":
                    goalBias = 60 - config.val  # retrieve the setting for
                    # each knob
                elif name == "goalTolerance":
                    goalTolerance = 11 - config.val  # retrieve the setting
                    # for each knob
                elif name == "stepSize":
                    stepSize = config.val  # retrieve the setting for each knob

        return [self.obj_path,
                str(obstacleDistance),
                str(trials),
                str(goalBias),
                str(goalTolerance),
                str(stepSize),
                "6",
                "30",
                "30",
                "363",
                "363"]

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
        f = open("./rrtout.txt", "r")
        stLine = float(f.readline())
        pthDist = float(f.readline())
        obDist = float(f.readline())
        closeness = float(f.readline())
        quality = abs(stLine / pthDist - obDist / pthDist) * 1 / math.sqrt(
            closeness + 1);
        return quality
