"""
This is an example file for prepraing Bodytrack for RAPID(C)
"""

from Classes import *  # import the parent class and other classes from the file Classes.py
from cs231n.data_utils import load_CIFAR10
from cs231n.classifiers.neural_net import TwoLayerNet
import numpy as np
import pickle


class appMethods(AppMethods):
    """ application specific class inherited from class AppMethods
    Please keep the name of the class to be appMethods since it will be used in RAPID(C) to create an instance of
    this class
    """

    bin_nn = "nn"  # the app binary to exec

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
            mv = self.checknn()
            # write the mv to file
            self.writeConfigMeasurementToFile(mvFact, configuration, mv)

            # backup the generated output to another location
            self.moveFile("./model_nn_w1.p",
                          "./training_outputs/output_nn_w1_" + str(float(learning) * 1e7) + "_" + str(
                              int(reg)) + "_" + str(int(batch)) + ".txt")
            self.moveFile("./model_nn_b1.p",
                          "./training_outputs/output_nn_b1_" + str(float(learning) * 1e7) + "_" + str(
                              int(reg)) + "_" + str(int(batch)) + ".txt")
            self.moveFile("./model_nn_w2.p",
                          "./training_outputs/output_nn_w2_" + str(float(learning) * 1e7) + "_" + str(
                              int(reg)) + "_" + str(int(batch)) + ".txt")
            self.moveFile("./model_nn_b2.p",
                          "./training_outputs/output_nn_b2_" + str(float(learning) * 1e7) + "_" + str(
                              int(reg)) + "_" + str(int(batch)) + ".txt")

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
        return [self.bin_nn,
                "--lr",
                str(learningRate),
                "--reg",
                str(regular),
                "--batch",
                str(batch)]

    def _get_test_data(self, num_training=49000, num_validation=1000, num_test=1000):
        """     
        Load the CIFAR-10 dataset from disk and perform preprocessing to prepare
        it for the two-layer neural net classifier. These are the same steps as
        we used for the SVM, but condensed to a single function.  
        """
        # Load the raw CIFAR-10 data
        cifar10_dir = '/home/liuliu/Research/ML/cs231n/datasets/cifar-10-batches-py'

        X_train, y_train, X_test, y_test = load_CIFAR10(cifar10_dir)

        # Subsample the data
        mask = list(range(num_training, num_training + num_validation))
        X_val = X_train[mask]
        y_val = y_train[mask]
        mask = list(range(num_training))
        X_train = X_train[mask]
        y_train = y_train[mask]
        mask = list(range(num_test))
        X_test = X_test[mask]
        y_test = y_test[mask]

        # Normalize the data: subtract the mean image
        mean_image = np.mean(X_train, axis=0)
        X_train -= mean_image
        X_val -= mean_image
        X_test -= mean_image

        # Reshape data to rows
        X_train = X_train.reshape(num_training, -1)
        X_val = X_val.reshape(num_validation, -1)
        X_test = X_test.reshape(num_test, -1)

        return X_test, y_test

    # helper function to evaluate the QoS
    def checknn(self):
        """
        In our example, after each run of the application, this function will be called to compare the current output
        with the groundtruth output.

        Two files both contains multiple rows where each row represents the calculated mean price for a swaption. We
        extract the mean price and calculate the distortion
        :return: a double value describing the QoS ( 0.0 ~ 100.0 )
        """

        X_test, y_test = self._get_test_data()

        input_size = 32 * 32 * 3
        hidden_size = 50
        num_classes = 10

        net = TwoLayerNet(input_size, hidden_size, num_classes)

        net.params['W1'] = pickle.load(open("model_nn_w1.p", "rb"))
        net.params['b1'] = pickle.load(open("model_nn_b1.p", "rb"))
        net.params['W2'] = pickle.load(open("model_nn_w2.p", "rb"))
        net.params['b2'] = pickle.load(open("model_nn_b2.p", "rb"))

        test_accuracy = (net.predict(X_test) == y_test).mean()

        print test_accuracy
        return test_accuracy
