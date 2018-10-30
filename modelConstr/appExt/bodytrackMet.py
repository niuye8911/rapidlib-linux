"""
This is an example file for prepraing Bodytrack for RAPID(C)
"""

from Classes import *  # import the parent class and other classes from the file Classes.py


class appMethods(AppMethods):
    input_path = "/home/liuliu/Research/mara_bench/parsec-3.0/pkgs/apps/bodytrack/run/sequenceB_261/"

    def train(self, config_table, costFact, mvFact, sysFact, withMV=False, withSys=False):
        configurations = config_table.configurations  # get the configurations in the table
        costFact = open(costFact, 'w')
        mvFact = open(mvFact, 'w')
        sysFact = open(sysFact, 'w')
        for configuration in configurations:
            cost = 0.0
            mv = 0.0
            configs = configuration.retrieve_configs()  # extract the configurations
            for config in configs:
                name = config.knob.set_name
                if name == "particle":
                    particle = config.val  # retrieve the setting for each knob
                elif name == "layer":
                    layer = config.val  # retrieve the setting for each knob

            # assembly the command
            command = self.get_command(str(particle), str(layer))

            # measure the "cost"
            cost, metric = self.getTime(command, 20, withSys)  # 20 jobs(bodytrack) per run
            # write the cost to file
            self.writeConfigMeasurementToFile(costFact, configuration, cost)

            # measure the "mv"
            if withMV:
                mv = self.checkBodytrack()
                self.writeConfigMeasurementToFile(mvFact, configuration, mv)
            if withSys:
                self.recordSysUsage(configuration, metric)
            # backup the generated output to another location
            self.moveFile(self.input_path + "poses.txt",
                          "./training_outputs/output_" + str(int(layer)) + "_" + str(int(particle)) + ".txt")
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
        print "GENERATING GROUND TRUTH for SWAPTIONS"
        command = self.get_command(4000, 5)
        defaultTime = self.getTime(command, 20)
        self.gt_path = "./training_outputs/grountTruth.txt"
        output_path = self.input_path + "poses.txt"
        self.moveFile(output_path, self.gt_path)
        print("The Default Execution time of Bodytrack" + " = " + str(defaultTime) + "ms")

    # helper function to assembly the command
    def get_command(self, numOfParticle, numOfLayer):
        return [self.obj_path,
                self.input_path,
                "4", "20",
                str(numOfParticle),
                str(numOfLayer),
                '4']

    # helper function to evaluate the QoS
    def checkBodytrack(self):
        """
        In our example, after each run of the application, this function will be called to compare the current output
        with the groundtruth output.

        Two files both contains multiple rows where each row represents the calculated mean price for a swaption. We
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
            print "DISTORTION = " + str(distortion)
            totDistortion += distortion
        return (1.0 - (totDistortion / len(truth_results))) * 100.0
