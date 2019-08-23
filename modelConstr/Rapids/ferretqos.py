class qos():
    gt_path="./training_outputs/groundTruth.txt"

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
            truthmap[name] = []
            for i in range(1, len(col)):  # 50 results
                truthmap[name].append(col[i].split(':')[0])
        #if len(missionmap) != len(truthmap):
        # mission failed in between
        #    print(len(missionmap), len(truthmap))
        #    return [0.0, 0.0, 0.0]
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
            try:
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
            except:
                print('ecpet')
                ranking_res = 0.0
                ranking = 0.0
                coverage = 0.0
            totAcuracy += ranking_res
            totRanking += ranking
            totCoverage += coverage
            S.clear()
            T.clear()
            Z.clear()
        print(totAcuracy / float(totimg))
        return [
            totCoverage / float(totimg), totRanking / float(totimg),
            totAcuracy / float(totimg)
        ]

q = qos()
q.getQoS()
