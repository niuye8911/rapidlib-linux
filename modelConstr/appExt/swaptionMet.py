"""
This is an example file for prepraing Swaptions for RAPID(C)
"""

from Classes import *  # import the parent class and other classes from the file Classes.py


class appMethods(AppMethods):
    """ application specific class inherited from class AppMethods
    Please keep the name of the class to be appMethods since it will be used in RAPID(C) to create an instance of
    this class
    """
    training_units = 20

    def cleanUpAfterEachRun(self, configs=None):
        num = 1000000
        if not configs == None:
            for config in configs:
                name = config.knob.set_name
                if name == "num":
                    num = config.val  # retrieve the setting for each knob
        # backup the generated output to another location
        self.moveFile("./output.txt", "./training_outputs/output" + str(int(num)) + ".txt")

    def afterGTRun(self):
        # generate the ground truth
        self.gt_path = "./training_outputs/grountTruth.txt"
        self.moveFile("./output.txt", self.gt_path)

    # helper function to assembly the command
    def getCommand(self, configs=None):
        num = 1000000
        if not configs == None:
            for config in configs:
                name = config.knob.set_name
                if name == "num":
                    num = config.val  # retrieve the setting for each knob
        print self.obj_path
        return [self.obj_path, "-ns", "10", "-sm", str(num)]

    # helper function to evaluate the QoS
    def getQoS(self):
        """
        In our example, after each run of the application, this function will be called to compare the current output
        with the groundtruth output.

        Two files both contains multiple rows where each row represents the calculated mean price for a swaption. We
        extract the mean price and calculate the distortion
        :return: a double value describing the QoS ( 0.0 ~ 100.0 )
        """
        gt_output = open(self.gt_path, "r")
        mission_output = open("./output.txt", "r")
        truth_map = {}
        mission_map = {}
        totalRound = 0
        for line in gt_output:
            col = line.split(':')
            round_num = col[0]
            round_res = float(col[1].split(',')[0])
            truth_map[round_num] = round_res
            totalRound += 1
        for line in mission_output:
            col = line.split(':')
            round_num = col[0]
            round_res = float(col[1].split(',')[0])
            mission_map[round_num] = round_res
        # calculate the distortion
        toterr = 0.0
        for round in range(0, totalRound):
            roundname = "round" + str(round)
            truth_res = truth_map[roundname]
            mission_res = mission_map[roundname]
            error = abs((truth_res - mission_res) / truth_res)
            toterr += error
        # write the average error
        meanQoS = 1 - toterr / totalRound
        meanQoS = meanQoS * 1000.0 - 999
        return meanQoS * 100.0
