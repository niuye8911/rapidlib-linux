import pickle

import numpy as np
from Classes import *
from cs231n.classifiers.neural_net import TwoLayerNet
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

    def cleanUpAfterEachRun(self, configs=None):
        learningRate = 100 * 1e-7
        regular = 25000
        batch = 500
        if configs is not None:
            for config in configs:
                name = config.knob.set_name
                if name == "learningRate":
                    learningRate = float(config.val) * 1e-7
                elif name == "regular":
                    regular = config.val * 100  # retrieve the setting for each
                    # knob
                elif name == "batch":
                    batch = 64 * pow(2,
                                     config.val - 1)  # retrieve the setting
                    # for each knob

        # backup the generated output to another location
        self.moveFile("./model_nn_w1.p", "./training_outputs/output_nn_w1_" +
                      str(float(learningRate) * 1e7) + "_" +
                      str(int(regular)) + "_" + str(int(batch)) + ".p")
        self.moveFile("./model_nn_b1.p", "./training_outputs/output_nn_b1_" +
                      str(float(learningRate) * 1e7) + "_" +
                      str(int(regular)) + "_" + str(int(batch)) + ".p")
        self.moveFile("./model_nn_w2.p", "./training_outputs/output_nn_w2_" +
                      str(float(learningRate) * 1e7) + "_" +
                      str(int(regular)) + "_" + str(int(batch)) + ".p")
        self.moveFile("./model_nn_b2.p", "./training_outputs/output_nn_b2_" +
                      str(float(learningRate) * 1e7) + "_" +
                      str(int(regular)) + "_" + str(int(batch)) + ".p")

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
                    regular = config.val * 100  # retrieve the setting for each
                    # knob
                elif name == "batch":
                    batch = config.val * 64  # retrieve the setting for each
                    # knob
        return [
            self.obj_path, "--lr",
            str(learningRate), "--reg",
            str(regular), "--batch",
            str(batch), "--train"
        ]

    def _get_test_data(self,
                       num_training=49000,
                       num_validation=1000,
                       num_test=1000):
        """
        Load the CIFAR-10 dataset from disk and perform preprocessing to prepare
        it for the two-layer neural net classifier. These are the same steps as
        we used for the SVM, but condensed to a single function.
        """
        # Load the raw CIFAR-10 data
        cifar10_dir = self.data_path

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
    def getQoS(self):
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

        print
        test_accuracy
        return test_accuracy
