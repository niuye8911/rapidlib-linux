"""
This is an example file for prepraing Bodytrack for RAPID(C)
"""

from Classes import *  # import the parent class and other classes from the file Classes.py
import numpy as np
from astar_qos_helper import solve
from ast import literal_eval
from mazes import Maze
from PIL import Image


class appMethods(AppMethods):
    """ application specific class inherited from class AppMethods
    Please keep the name of the class to be appMethods since it will be used in RAPID(C) to create an instance of
    this class
    """

    bin_astar = "astar"  # the app binary to exec

    def train(self, config_table, costFact, mvFact):
        """ Override the train()

        The purpose of this application is to get the cost and mv for each configuration. It will iterate through all
        configurations in config_table and run the app with each of them. The developers are responsible to implement
        their own logic to measure the Cost and QoS.

        The output will be written to costFact and mvFact

        In this example, the Cost is the execution time and the QoS is the distortion

        :param config_table: the configuration table is an object of class Profile, containing all configurations,
        :param costFact: the path to cost.fact
        :param mvFact: the path to mv.fact
        """
        configurations = config_table.configurations  # get the configurations in the table
        costFact = open(costFact, 'w')
        mvFact = open(mvFact, 'w')

        # iterate through configurations
        for configuration in configurations:
            # the purpose of each iteration is to fill in the two values below
            cost = 0.0
            mv = 0.0
            configs = configuration.retrieve_configs()  # extract the configurations

            # fetch the concrete setting(s)
            for config in configs:
                name = config.knob.set_name
                print name
                if name == "method":
                    method = config.val  # retrieve the setting for each knob
                elif name == "cutover":
                    print "found cutover"
                    cutOver = config.val  # retrieve the setting for each knob
                elif name == "threshold":
                    threshold = config.val

            # assembly the command
            command = self.get_command(method, cutOver, threshold)
            print command

            # measure the "cost"
            cost = self.getTime(command, 5)  # 10 jobs(particle) per run
            # write the cost to file
            self.writeConfigMeasurementToFile(costFact, configuration, cost)

            # measure the "mv"
            mv = self.checkastar()
            # write the mv to file
            self.writeConfigMeasurementToFile(mvFact, configuration, mv)

            # backup the generated output to another location
            self.moveFile("./results.txt", "./training_outputs/trash.txt")

        costFact.close()
        mvFact.close()

    def runGT(self):
        """ Override the runGT()

        The purpose of this function is to generate the groundtruth for the application. This function will be called
        once before calling train()

        In our example, we generate the output of the application when running in default mode and move it to
        somewhere else
        """
        # SVM's QoS does not depend on a grounttruth, so pass
        pass

    # helper function to assembly the command
    def get_command(self, cutOver, method, threshold):
        return [self.bin_astar,
                "--method",
                str(method),
                "--cutover",
                str(cutOver),
                "--threshold",
                str(threshold)]

    # helper function to evaluate the QoS
    def checkastar(self):
        """
        In our example, after each run of the application, this function will be called to compare the current output
        with the groundtruth output.

        Two files both contains multiple rows where each row represents the calculated mean price for a swaption. We
        extract the mean price and calculate the distortion
        :return: a double value describing the QoS ( 0.0 ~ 100.0 )
        """
        with open("results.txt", "r") as file:
            content = file.readlines();

        content = [x.strip() for x in content]
        item = content[2]

        for item in content:
            vals = item.split("#")

            file = vals[0]
            end_point = literal_eval(vals[2])
            real_length = int(vals[1])

            im = Image.open(file)
            maze = Maze(im)

            optimal_length = solve(maze)

            remaining_length = 0

            width = maze.width

            if cmp(end_point, maze.end.Position) == 0:
                remaining_length = 0
            else:
                # new_maze = Maze(im, end_point)
                end_node = maze.all_nodes[end_point[0] * width + end_point[1]]
                remaining_length = solve(maze, end_node)
            # remaining_length = abs(end_point[0] - maze.end.Position[0]) + abs(end_point[1] - maze.end.Position[1])

            print "Optimal length " + str(optimal_length)
            print "Real length " + str(real_length)
            print "Remaining legnth " + str(remaining_length)

            qos = optimal_length / (real_length + (remaining_length * 1.5))

            print "QOS " + str(qos)
            return float(qos)
