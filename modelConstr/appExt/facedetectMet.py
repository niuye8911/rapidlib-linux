"""
This is an example file for prepraing Bodytrack for RAPID(C)
"""

from Classes import *  # import the parent class and other classes from the


# file Classes.py


class appMethods(AppMethods):
    image_index_path = "/home/liuliu/Research/mara_bench/face-detect/pics" \
                       "/pic_index/training.txt"
    pic_path = "/home/liuliu/Research/mara_bench/face-detect/pics/"
    evaluation_obj_path = "/home/liuliu/Research/mara_bench/face-detect" \
                          "/evaluation/evaluate"
    grond_truth_path = "/home/liuliu/Research/mara_bench/face-detect/pics" \
                       "/pic_index/training_result.txt"

    def __init__(self, name, obj_path):
        """ Initialization with app name
        :param name:
        """
        AppMethods.__init__(self, name, obj_path)
        self.training_units = 50

    def cleanUpAfterEachRun(self, configs=None):
        # backup the generated output to another location
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

        self.moveFile("./result.txt",
                      "./training_outputs/result_" + str(pyramid) + "_" + str(
                          selectivity) + "_" + str(eyes) + ".txt")

    def afterGTRun(self):
        self.gt_path = "./training_outputs/grountTruth.txt"
        output_path = "./result.txt"
        self.moveFile(output_path, self.gt_path)

    # helper function to assembly the command
    def getCommand(self, configs=None):
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
        return [self.obj_path,
                "-index",
                self.image_index_path,
                '-p',
                str(pyramid),
                '-s',
                str(selectivity),
                '-e',
                str(eyes)]

    def computeQoSWeight(self, preferences, values):
        # preferences is the preferecne and values contains the raw mv weight
        precision = float(values[0])
        recall = float(values[1])
        precision_pref = float(preferences[0])
        recall_pref = float(preferences[1])
        normalization = (precision_pref + recall_pref) / \
                        (precision_pref * recall_pref)
        print
        normalization, preferences, values
        return 100.0 * normalization * precision_pref * precision * \
               recall_pref * recall / (
                       precision * precision_pref + recall_pref * recall)

    # helper function to evaluate the QoS
    def getQoS(self):
        # run the evaluation routine
        evaluate_cmd = [
            self.evaluation_obj_path,
            '-a',
            self.grond_truth_path,
            '-d',
            './result.txt',
            '-f',
            '0',
            '-i',
            self.pic_path,
            '-l',
            self.image_index_path,
            '-z',
            '.jpg'
        ]
        os.system(" ".join(evaluate_cmd))
        # get the precision and recall
        result = open('./tempDiscROC.txt', 'r')
        # call evaluate routine
        for line in result:
            col = line.split()
            recall = float(col[0])
            precision = float(col[1])
            break
        return [precision, recall,
                100.0 * 2 * precision * recall / (precision + recall)]
