"""
This is an example file for prepraing Bodytrack for RAPID(C)
"""

import os

from Rapids_Classes.AppMethods import AppMethods  # import the parent class and other classes


class appMethods(AppMethods):
    image_index_path = "/home/liuliu/Research/mara_bench/mara_face/pics" \
                       "/pic_index/training100.txt"
    image_index_full_path = "/home/liuliu/Research/mara_bench/mara_face" \
                            "/pics" \
                            "/pic_index/full400.txt"
    pic_path = "/home/liuliu/Research/mara_bench/mara_face/pics/"
    evaluation_obj_path = "/home/liuliu/Research/mara_bench/mara_face" \
                          "/evaluation/evaluate"
    full_grond_truth_path = "/home/liuliu/Research/mara_bench/mara_face/pics" \
                       "/pic_index/full400_result.txt"
    train_grond_truth_path = "/home/liuliu/Research/mara_bench/mara_face/pics" \
                       "/pic_index/training100_result.txt"

    def __init__(self, name, obj_path):
        """ Initialization with app name
        :param name:
        """
        AppMethods.__init__(self, name, obj_path)
        self.training_units = 100
        self.fullrun_units = 400
        self.max_cost = 1000
        self.min_cost = 30
        self.min_mv = 0
        self.max_mv = 142
        self.gt_path = self.train_grond_truth_path  # default is training
        self.run_config_file = ''

    def cleanUpAfterEachRun(self, configs=None):
        # backup the generated output to another location
        pyramid = 20
        selectivity = 2
        eyes = 2
        if configs is not None:
            for config in configs:
                name = config.knob.set_name
                if name == "pyramid":
                    pyramid = config.val  # retrieve the setting for each knob
                elif name == "selectivity":
                    selectivity = config.val  # retrieve the setting for each
                    # knob
                elif name == "eyes":
                    eyes = config.val  # retrieve the setting for each knob

        self.moveFile(
            self.run_dir + "result.txt",
            self.run_dir + "training_outputs/result_" + str(pyramid) + "_" +
            str(selectivity) + "_" + str(eyes) + ".txt")

    def afterGTRun(self):
        pass

    def getRapidsCommand(self):
        self.gt_path = self.full_grond_truth_path
        if not os.path.exists(self.run_config):
            print("no config file exists:", self.appName, self.run_config)
            return []
        cmd = [
            self.obj_path, "-index", self.image_index_full_path, "-rsdg",
            self.run_config, '1>/dev/null'
        ]
        return cmd

    # helper function to assembly the command
    def getCommand(self, configs=None, qosRun=False, fullRun=False):
        if qosRun:
            return []  # return dummy command
        if fullRun or qosRun:
            self.gt_path = self.full_grond_truth_path
        pyramid = 25
        selectivity = 2
        eyes = 2
        if configs is not None:
            for config in configs:
                name = config.knob.set_name
                if name == "pyramid":
                    pyramid = config.val  # retrieve the setting for each knob
                elif name == "selectivity":
                    selectivity = config.val  # retrieve the setting for each
                    # knob
                elif name == "eyes":
                    eyes = config.val  # retrieve the setting for each knob
        index = self.image_index_full_path if (
            qosRun or fullRun) else self.image_index_path
        return [
            self.obj_path, "-index", index, '-p',
            str(pyramid), '-s',
            str(selectivity), '-e',
            str(eyes)
        ]

    def computeQoSWeight(self, preferences, values):
        # preferences is the preferecne and values contains the raw mv weight
        precision = float(values[0])
        recall = float(values[1])
        precision_pref = float(preferences[0])
        recall_pref = float(preferences[1])
        beta = recall_pref / precision_pref
        normalization = 1 + beta * beta
        weighted_score = 100.0 * normalization * precision * recall / (
            beta * beta * precision + recall)
        # default_score = 100.0 * 2 * precision * recall / (precision+recall)
        return weighted_score

    # helper function to evaluate the QoS
    def getQoS(self):
        # run the evaluation routine
        if self.gt_path == self.full_grond_truth_path:
            indexfile = self.image_index_full_path
        else:
            indexfile = self.image_index_path
        evaluate_cmd = [
            self.evaluation_obj_path, '-a', self.gt_path, '-d',
            self.run_dir + 'result.txt', '-f', '0', '-i', self.pic_path, '-l',
            indexfile, '-z', '.jpg'
        ]
        try:
            os.system(" ".join(evaluate_cmd))
            # get the precision and recall
            result = open(self.run_dir + 'tempDiscROC.txt', 'r')
            # call evaluate routine
            for line in result:
                col = line.split()
                recall = float(col[0])
                precision = float(col[1])
                break
        except:
            return [0.0, 0.0, 0.0]
        return [
            precision, recall,
            100.0 * 1.09 * precision * recall / (0.09 * precision + recall)
        ]
