"""
This is an example file for prepraing Swaptions for RAPID(C)
"""

from Rapids_Classes.AppMethods import AppMethods  # import the parent class and other classes from the
import os

# file Classes.py


class appMethods(AppMethods):
    """ application specific class inherited from class AppMethods
    Please keep the name of the class to be appMethods since it will be used
    in RAPID(C) to create an instance of
    this class
    """

    def __init__(self, name, obj_path):
        """ Initialization with app name
        :param name:
        """
        AppMethods.__init__(self, name, obj_path)
        self.training_units = 20
        self.fullrun_units = 50
        self.max_cost = 2204
        self.min_cost = 22
        self.min_mv = 85.67
        self.max_mv = 100
        self.gt_path = "./training_outputs/swap-gt.txt"

    def cleanUpAfterEachRun(self, configs=None):
        num = 1000000
        if configs is not None:
            for config in configs:
                name = config.knob.set_name
                if name == "num":
                    num = config.val  # retrieve the setting for each knob
        # backup the generated output to another location
        self.moveFile("./output.txt",
                      "./training_outputs/output" + str(int(num)) + ".txt")

    def afterGTRun(self):
        # generate the ground truth
        if not os.path.exists(self.gt_path):
            self.moveFile("./output.txt", self.gt_path)

    def getFullRunCommand(self, budget, xml='', OFFLINE=False, UNIT=-1):
        xml_path = xml if xml != '' else "./outputs/" + self.appName + "-default.xml"
        if UNIT==-1:
            unit = 10000 # arbiturary large, then no reconfig
        else:
            unit = max(1,int(self.fullrun_units / UNIT))
        cmd = [
            self.obj_path, "-ns",
            str(self.fullrun_units), "-sm", "100", "-rsdg", "-cont", "-b",
            str(budget), "-xml", xml_path, "-u", str(unit)
        ]
        if OFFLINE:
            cmd = cmd + ['-offline']
        print(" ".join(cmd))
        return cmd

    # helper function to assembly the command
    def getCommand(self, configs=None, qosRun=False, fullRun=True):
        if qosRun and os.path.exists(self.gt_path):
            return ['ls']  # return dummy command
        num = 1000000
        if qosRun or fullRun:
            units = self.fullrun_units
        else:
            units = self.training_units
        if configs is not None:
            for config in configs:
                name = config.knob.set_name
                if name == "num":
                    num = config.val  # retrieve the setting for each knob
        return [self.obj_path, "-ns", str(units), "-sm", str(num)]

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
        return (meanQoS * 100.0 - 99.9) * 1000
