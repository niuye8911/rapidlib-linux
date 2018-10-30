"""
This is an example file for prepraing Swaptions for RAPID(C)
"""

from Classes import *  # import the parent class and other classes from the file Classes.py


class appMethods(AppMethods):
    """ application specific class inherited from class AppMethods
    Please keep the name of the class to be appMethods since it will be used in RAPID(C) to create an instance of
    this class
    """

    def train(self, config_table, costFact, mvFact, sysFact, withMV=False, withSys=False):
        """ Override the train()

        The purpose of this application is to get the cost and mv for each configuration. It will iterate through all
        configurations in config_table and run the app with each of them. The developers are responsible to implement
        their own logic to measure the Cost and QoS.

        The output will be written to costFact and mvFact

        In this example, the Cost is the execution time and the QoS is the distortion

        :param config_table: the configuration table is an object of class Profile, containing all configurations,
        :param costFact: the path to cost.fact
        :param mvFact: the path to mv.fact
        :param withSys: with or without recording system usage
        """
        configurations = config_table.configurations  # get the configurations in the table
        costFact = open(costFact, 'w')
        mvFact = open(mvFact, 'w')
        sysFact = open(sysFact, 'w')

        # iterate through configurations
        for configuration in configurations:
            self.pinTime(costFact);
            # the purpose of each iteration is to fill in the two values below
            cost = 0.0
            mv = 0.0
            configs = configuration.retrieve_configs()  # extract the configurations

            # fetch the concrete setting(s)
            for config in configs:
                name = config.knob.set_name
                if name == "num":
                    num = config.val  # retrieve the setting for each knob

            # assembly the command
            command = self.get_command(str(num))

            # measure the "cost"
            cost, metric = self.getTime(command, 10, withSys, configuration.printSelf('-'))  # 10 jobs(swaption) per run
            # write the cost to file
            self.writeConfigMeasurementToFile(costFact, configuration, cost)

            # measure the "mv"
            if withMV:
                mv = self.checkSwaption()
                # write the mv to file
                self.writeConfigMeasurementToFile(mvFact, configuration, mv)
            if withSys:
                # write metric value to table
                self.recordSysUsage(configuration, metric)
            # backup the generated output to another location
            self.moveFile("./output.txt", "./training_outputs/output" + str(int(num)) + ".txt")
        # write the metric to file
        if withSys:
            self.printUsageTable(sysFact)
        costFact.close()
        mvFact.close()

    def runGT(self):
        """ Override the runGT()

        The purpose of this function is to generate the groundtruth for the application. This function will be called
        once before calling train()

        In our example, we generate the output of the application when running in default mode and move it to
        somewhere else
        """
        # generate the ground truth
        print
        "GENERATING GROUND TRUTH for SWAPTIONS"
        command = self.get_command(1000000)
        defaultTime = self.getTime(command, 10)
        self.gt_path = "./training_outputs/grountTruth.txt"
        self.moveFile("./output.txt", self.gt_path)
        print("The Default Execution time of Swaptions" + " = " + str(defaultTime) + "ms")

    # helper function to assembly the command
    def get_command(self, numOfSim):
        return [self.obj_path, "-ns", "10", "-sm", str(numOfSim)]

    # helper function to evaluate the QoS
    def checkSwaption(self):
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
