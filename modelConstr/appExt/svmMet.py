"""
This is an example file for prepraing SVM for RAPID(C)
"""

import pickle

import numpy as np
from Classes import *
from cs231n.classifiers import LinearSVM
from cs231n.data_utils import load_CIFAR10


class appMethods(AppMethods):
    data_path = "/home/liuliu/Research/mara_bench/machine_learning/cs231n" \
                "/datasets/cifar-10-batches-py"

    def __init__(self, name, obj_path):
        """ Initialization with app name
        :param name:
        """
        AppMethods.__init__(self, name, obj_path)
        self.training_units = 1
        self.fullrun_units = 10
        self.max_cost = 3746
        self.min_cost = 2230

    def cleanUpAfterEachRun(self, configs=None):
        learningRate = 100 * 1e-7
        regular = 25000
        batch = 500
        if configs is None:
            # no ground truth
            pass
        if configs is not None:
            for config in configs:
                name = config.knob.set_name
                if name == "learningRate":
                    learningRate = float(config.val) * 1e-7
                elif name == "regular":
                    regular = config.val * 5000  # retrieve the setting for each
                    # knob
                elif name == "batch":
                    batch = 64 * pow(2,
                                     config.val - 1)  # retrieve the setting
                    # for each knob

        # backup the generated output to another location
        self.moveFile("./model_svm.p",
                      "./training_outputs/output_" + str(
                          float(learningRate) * 1e7) + "_" + str(
                          int(regular)) + "_" + str(
                          int(batch)) + ".txt")

    def getFullRunCommand(self, budget):
        return [self.obj_path,
                "--rsdg", "-cont",
                "-b", str(budget),
                "-xml", "./outputs/" + self.appName + "-default.xml",
                "-u", '1']

    # helper function to assembly the command
    def getCommand(self, configs=None, qosRun=False):
        learningRate = 100 * 1e-7
        regular = 25000
        batch = 500
        if configs is not None:
            for config in configs:
                name = config.knob.set_name
                if name == "learningRate":
                    learningRate = float(config.val) * 1e-7
                elif name == "regular":
                    regular = config.val * 5000  # retrieve the setting for each
                    # knob
                elif name == "batch":
                    batch = 64 * pow(2,
                                     config.val - 1)  # retrieve the setting
                    # for each knob
        return [self.obj_path,
                "--lr",
                str(learningRate),
                "--reg",
                str(regular),
                "--batch",
                str(batch),
                "--train"]

    # helper function to evaluate the QoS
    def getQoS(self):
        X_train, y_train, X_test, y_test = load_CIFAR10(self.data_path)

        X_test = np.reshape(X_test, (X_test.shape[0], -1))
        X_train = np.reshape(X_train, (X_train.shape[0], -1))

        mean_image = np.mean(X_train, axis=0)

        X_test -= mean_image
        X_test = np.hstack([X_test, np.ones((X_test.shape[0], 1))])
        svm = LinearSVM()
        svm.W = pickle.load(open("./model_svm.p", "rb"))
        y_test_pred = svm.predict(X_test)
        test_accuracy = np.mean(y_test == y_test_pred)
        return test_accuracy