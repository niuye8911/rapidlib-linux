import pickle

import numpy as np
from Rapids_Classes.AppMethods import AppMethods
from cs231n.classifiers.neural_net import TwoLayerNet
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
        self.max_cost = 3126
        self.min_cost = 2597
        self.min_mv = 7.2
        self.max_mv = 18.3

    def cleanUpAfterEachRun(self, configs=None):
        learningRate = 100 * 1e-5
        regular = 0.05
        batch = 500
        if configs is not None:
            for config in configs:
                name = config.knob.set_name
                if name == "learning":
                    learningRate = float(config.val) * 1e-5
                elif name == "regular":
                    regular = config.val * 0.05  # retrieve the setting for each
                    # knob
                elif name == "batch":
                    batch = 64 * pow(2, config.val - 1)  # retrieve the setting
                    # for each knob

        # backup the generated output to another location
        #self.moveFile("./model_nn_w1.p", "./training_outputs/output_nn_w1_" +
        #              str(float(learningRate) * 1e-7) + "_" +

    #                  str(int(regular)) + "_" + str(int(batch)) + ".p")
    #    self.moveFile("./model_nn_b1.p", "./training_outputs/output_nn_b1_" +


#                      str(float(learningRate) * 1e-7) + "_" +
#str(int(regular)) + "_" + str(int(batch)) + ".p")
#self.moveFile("./model_nn_w2.p", "./training_outputs/output_nn_w2_" +
#str(float(learningRate) * 1e-7) + "_" +
#str(int(regular)) + "_" + str(int(batch)) + ".p")
#self.moveFile("./model_nn_b2.p", "./training_outputs/output_nn_b2_" +
#str(float(learningRate) * 1e-7) + "_" +
#str(int(regular)) + "_" + str(int(batch)) + ".p")

    def getRapidsCommand(self):
        if not os.path.exists(self.run_config):
            print("no config file exists:", self.appName, self.run_config)
            return []
        return [
            self.obj_path,
            "-rsdg",
            self.run_config  #,'1>/dev/null'
        ]

    # helper function to assembly the command
    def getCommand(self, configs=None, qosRun=False, fullRun=True):
        if qosRun:
            return []
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
                        int(config.val) - 1)  # retrieve the setting for each
                    # knob
        print(" ".join([
            self.obj_path, "--lr",
            str(learningRate), "--reg",
            str(regular), "--batch",
            str(batch), "" if (qosRun or fullRun) else "-train"
        ]))
        return [
            self.obj_path, "--lr",
            str(learningRate), "--reg",
            str(regular), "--batch",
            str(batch), "" if (qosRun or fullRun) else "-train"
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
        hidden_size = 110
        num_classes = 10

        net = TwoLayerNet(input_size, hidden_size, num_classes)
        try:
            net.params['W1'] = pickle.load(open(self.run_dir + "model_nn_w1.p",
                                                "rb"),
                                           encoding='latin1')
            net.params['b1'] = pickle.load(open(self.run_dir + "model_nn_b1.p",
                                                "rb"),
                                           encoding='latin1')
            net.params['W2'] = pickle.load(open(self.run_dir + "model_nn_w2.p",
                                                "rb"),
                                           encoding='latin1')
            net.params['b2'] = pickle.load(open(self.run_dir + "model_nn_b2.p",
                                                "rb"),
                                           encoding='latin1')

            test_accuracy = (net.predict(X_test) == y_test).mean()
        except:
            test_accuracy = 0.0
        print("qos", str(test_accuracy))
        return test_accuracy * 100.0
