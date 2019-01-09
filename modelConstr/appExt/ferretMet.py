"""
This is an example file for prepraing Bodytrack for RAPID(C)
"""

from Classes import *  # import the parent class and other classes from the


# file Classes.py


class appMethods(AppMethods):
    database_path = "/home/liuliu/Research/mara_bench/parsec-3.0/pkgs/apps" \
                    "/ferret/run/corelnative/"
    table = "lsh"
    query_path = "/home/liuliu/Research/mara_bench/parsec-3.0/pkgs/apps" \
                 "/ferret/run/queries"
    fullrun_query_path = "/home/liuliu/Research/mara_bench/parsec-3.0/pkgs" \
                         "/apps/ferret/run/queriesnative"

    def __init__(self, name, obj_path):
        """ Initialization with app name
        :param name:
        """
        AppMethods.__init__(self, name, obj_path)
        self.training_units = 20
        self.fullrun_units = 1000
        self.max_cost = 182
        self.min_cost = 91

    def cleanUpAfterEachRun(self, configs=None):
        # backup the generated output to another location
        itr = 25
        hash = 8
        probe = 20
        if configs is not None:
            for config in configs:
                name = config.knob.set_name
                if name == "hash":
                    hash = config.val  # retrieve the setting for each knob
                elif name == "probe":
                    probe = config.val  # retrieve the setting for each knob
                elif name == "itr":
                    itr = config.val  # retrieve the setting for each knob

        self.moveFile("output.txt",
                      "./training_outputs/output_" + str(hash) + "_" + str(
                          probe) + "_" + str(itr) + ".txt")

    def afterGTRun(self):
        self.gt_path = "./training_outputs/groundTruth.txt"
        output_path = "output.txt"
        self.moveFile(output_path, self.gt_path)

    def getFullRunCommand(self, budget):
        return [self.obj_path,
                self.database_path,
                self.table,
                self.fullrun_query_path,
                "50", "20", "1", "output.txt",
                "-rsdg", "-cont",
                "-b", str(budget),
                "-xml", "./outputs/" + self.appName + "-default.xml",
                "-u", '300']

    # helper function to assembly the command
    def getCommand(self, configs=None, qosRun=False):
        itr = 25
        hash = 8
        probe = 20
        if configs is not None:
            for config in configs:
                name = config.knob.set_name
                if name == "hash":
                    hash = config.val  # retrieve the setting for each knob
                elif name == "probe":
                    probe = config.val  # retrieve the setting for each knob
                elif name == "itr":
                    itr = config.val  # retrieve the setting for each knob
        if qosRun:
            query_path = self.fullrun_query_path
        else:
            query_path = self.query_path
        return [self.obj_path,
                self.database_path,
                self.table, query_path,
                "50",
                "20",
                "1",
                "output.txt",
                '-l',
                str(hash),
                '-t',
                str(probe),
                '-itr',
                str(itr)]

    def computeQoSWeight(self, preferences, values):
        # preferences is the preferecne and values contains the raw mv weight
        ranking = values[1]
        coverage = values[0]
        ranking_pref = preferences[1]
        coverage_pref = preferences[0]
        maxError = (2 * coverage_pref - ranking_pref) * 50 * 51
        # 50 images in real run
        ranking_res = (1.0 + (
                ranking_pref * ranking + 2 * coverage_pref * coverage) /
                       float(
                           maxError)) * 100.0
        return ranking_res

    def rank(self, img, imglist):
        if img in imglist:
            return imglist.index(img) + 1
        return 0

    def compute1(self, list1, imgset):
        res = 0
        for img in imgset:
            res += self.rank(img, list1)
        return res

    def compute2(self, list1, list2, imgset):
        res = 0
        for img in imgset:
            res += abs(self.rank(img, list1) - self.rank(img, list2))
        return res

    # helper function to evaluate the QoS
    def getQoS(self):
        truth = open(self.gt_path, "r")
        mission = open("./output.txt", "r")
        truthmap = {}
        missionmap = {}
        truth_res = []
        mission_res = []
        # check if both file contains the same number of lines
        for line in mission:
            col = line.split('\t')
            name = col[0].split("/")[-1]
            missionmap[name] = []
            for i in range(1, len(col)):  # 50 results
                missionmap[name].append(col[i].split(':')[0])
        for line in truth:
            col = line.split('\t')
            name = col[0].split("/")[-1]
            if name not in missionmap:
                continue
            truthmap[name] = []
            for i in range(1, len(col)):  # 50 results
                truthmap[name].append(col[i].split(':')[0])
        if len(missionmap) != len(truthmap):
            # mission failed in between
            print
            len(missionmap), len(truthmap)
            return [0.0, 0.0, 0.0]
        # now that 2 maps are set, compare each item
        # setup the Z / S/ and T
        Z = set()
        S = set()
        T = set()
        totAcuracy = 0.0
        totCoverage = 0.0
        totRanking = 0.0
        totimg = 0.0
        for query_image in truthmap:
            totimg += 1.0
            truth_res = truthmap[query_image]
            mission_res = missionmap[query_image]
            # compute the worst case senario, where Z = empty
            maxError = len(truth_res) * (len(truth_res) + 1)
            # setup S and T
            S.update(truth_res)
            T.update(mission_res)
            Z = S & T  # Z includes images both in S and T
            # clear S and T
            for s in Z:
                T.remove(s)
                S.remove(s)
            # now that Z, S, and T are set, compute the ranking function
            # two Sub QoS
            coverage = -1 * (len(truth_res) - len(Z)) * (len(truth_res) + 1)
            ranking = -1 * (self.compute2(truth_res, mission_res,
                                          Z) - self.compute1(truth_res,
                                                             S) - self.compute1(
                mission_res, T))
            ranking_res = (1.0 + (2 * coverage + ranking) / float(
                maxError)) * 100.0

            totAcuracy += ranking_res
            totRanking += ranking
            totCoverage += coverage
            S.clear()
            T.clear()
            Z.clear()
            print[totCoverage / float(totimg),
                  totRanking / float(totimg),
                  totAcuracy / float(totimg)]
        return [totCoverage / float(totimg),
                totRanking / float(totimg),
                totAcuracy / float(totimg)]
