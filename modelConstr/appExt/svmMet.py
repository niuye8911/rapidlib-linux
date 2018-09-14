"""
This is an example file for prepraing Bodytrack for RAPID(C)
"""

from Classes import *  # import the parent class and other classes from the file Classes.py
from cs231n.data_utils import load_CIFAR10
from cs231n.classifiers import LinearSVM
import numpy as np
import pickle


class appMethods(AppMethods):
    """ application specific class inherited from class AppMethods
    Please keep the name of the class to be appMethods since it will be used in RAPID(C) to create an instance of
    this class
    """

    bin_svm = "rapid_svm"  # the app binary to exec

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
                if name == "learning":
                    learning = float(config.val) * 1e-7  # retrieve the setting for each knob
                elif name == "regular":
                    reg = config.val  # retrieve the setting for each knob
                elif name == "batch":
                    batch = config.val

            # assembly the command
            command = self.get_command(learning, reg, batch)
            print command

            # measure the "cost"
            cost = self.getTime(command, 10)  # 10 jobs(particle) per run
            # write the cost to file
            self.writeConfigMeasurementToFile(costFact, configuration, cost)

            # measure the "mv"
            mv = self.checksvm()
            # write the mv to file
            self.writeConfigMeasurementToFile(mvFact, configuration, mv)

            # backup the generated output to another location
            self.moveFile("./model_svm.p",
                          "./training_outputs/output_" + str(float(learning) * 1e7) + "_" + str(int(reg)) + "_" + str(
                              int(batch)) + ".txt")

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
    def get_command(self, learningRate, regular, batch):
        return [self.bin_svm,
                "--lr",
                str(learningRate),
                "--reg",
                str(regular),
                "--batch",
                str(batch)]

    # helper function to evaluate the QoS
    def checksvm(self):
        """
        In our example, after each run of the application, this function will be called to compare the current output
        with the groundtruth output.

        Two files both contains multiple rows where each row represents the calculated mean price for a swaption. We
        extract the mean price and calculate the distortion
        :return: a double value describing the QoS ( 0.0 ~ 100.0 )
        """
        cifar10_dir = '/home/liuliu/Research/ML/cs231n/datasets/cifar-10-batches-py'
        X_train, y_train, X_test, y_test = load_CIFAR10(cifar10_dir)

        X_test = np.reshape(X_test, (X_test.shape[0], -1))
        X_train = np.reshape(X_train, (X_train.shape[0], -1))

        mean_image = np.mean(X_train, axis=0)

        X_test -= mean_image
        X_test = np.hstack([X_test, np.ones((X_test.shape[0], 1))])
        svm = LinearSVM()
        svm.W = pickle.load(open("./model_svm.p", "rb"))
        y_test_pred = svm.predict(X_test)
        test_accuracy = np.mean(y_test == y_test_pred)
        print test_accuracy
        return test_accuracy
