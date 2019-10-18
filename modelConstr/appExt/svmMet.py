"""
This is an example file for prepraing SVM for RAPID(C)
"""

import pickle
import os
import numpy as np
from Rapids_Classes.AppMethods import AppMethods
from cs231n.classifiers import LinearSVM
from cs231n.data_utils import load_CIFAR10


class appMethods(AppMethods):
    data_path = "/home/liuliu/Research/mara_bench/mara_learn/cs231n" \
                "/datasets/cifar-10-batches-py"

    def __init__(self, name, obj_path):
        """ Initialization with app name
        :param name:
        """
        AppMethods.__init__(self, name, obj_path)
        self.training_units = 5
        self.fullrun_units = 10
        self.max_cost = 3563
        self.min_cost = 2529
        self.min_mv = 20.56
        self.max_mv = 33.78
        self.run_config = './outputs/svm/svm_run.config'

    def cleanUpAfterEachRun(self, configs=None):
        learningRate = 100 * 1e-5
        regular = 0.05
        batch = 500
        if configs is None:
            # no ground truth
            pass
        if configs is not None:
            for config in configs:
                name = config.knob.set_name
                if name == "learning":
                    learningRate = float(config.val) * 1e-5
                elif name == "regular":
                    regular = float(
                        config.val) * 0.05  # retrieve the setting for each
                    # knob
                elif name == "batch":
                    batch = 64 * pow(
                        2,
                        int(config.val) - 1)  # retrieve the setting
                    # for each knob

        # backup the generated output to another location
        #self.moveFile("./model_svm.p",
        #              "./training_outputs/output_" + str(
        #                  float(learningRate) * 1e-5) + "_" + str(
        #                  int(regular)) + "_" + str(
        #                  int(batch)) + ".txt")

    def getRapidsCommand(self):
        if not os.path.exists(self.run_config):
            print("no config file exists:",self.appName,self.run_config)
            return []
        cmd = [
            self.obj_path, "-rsdg", self.run_config
        ]
        return cmd

    # helper function to assembly the command
    def getCommand(self, configs=None, qosRun=False, fullRun=True):
        if qosRun:
            return ['ls']
        learningRate = 100 * 1e-5
        regular = 0.05
        batch = 500
        if configs is not None:
            for config in configs:
                name = config.knob.set_name
                if name == "learning":
                    learningRate = float(config.val) * 1e-5
                elif name == "regular":
                    regular = float(
                        config.val) * 0.05  # retrieve the setting for each
                    # knob
                elif name == "batch":
                    batch = 64 * pow(
                        2,
                        int(config.val) - 1)  # retrieve the setting
                    # for each knob
        return [
            self.obj_path, "--lr",
            str(learningRate), "--reg",
            str(regular), "--batch",
            str(batch), "" if (qosRun or fullRun) else "-train"
        ]

    # helper function to evaluate the QoS
    def getQoS(self):
        X_train, y_train, X_test, y_test = load_CIFAR10(self.data_path)

        X_test = np.reshape(X_test, (X_test.shape[0], -1))
        X_train = np.reshape(X_train, (X_train.shape[0], -1))

        mean_image = np.mean(X_train, axis=0)

        X_test -= mean_image
        X_test = np.hstack([X_test, np.ones((X_test.shape[0], 1))])
        svm = LinearSVM()
        try:
            svm.W = pickle.load(open("./model_svm.p", "rb"), encoding='latin1')
            y_test_pred = svm.predict(X_test)
            test_accuracy = np.mean(y_test == y_test_pred)
        except:
            test_accuracy = 0.0
        return test_accuracy * 100.0
