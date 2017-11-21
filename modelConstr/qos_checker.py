"""QOS loss checker for all apps"""

#QOS checker for ferret
def checkFerret(fact, observed):
    truth = open(fact, "r")
    mission = open(observed, "r")
    truthmap = {}
    missionmap = {}
    truth_res = []
    mission_res = []
    qos_report = open("qos_report", "w")
    for line in truth:
        col = line.split('\t')
        name = col[0].split("//")[1]
        truthmap[name] = []
        for i in range(1,len(col)): # 50 results
            truthmap[name].append(col[i].split(':')[0])
    for line in mission:
        col = line.split('\t')
        name = col[0].split("/")[1]
        missionmap[name] = []
        for i in range(1, len(col)):  # 50 results
            missionmap[name].append(col[i].split(':')[0])
    # now that 2 maps are set, compare each item
    # setup the Z / S/ and T
    Z = set()
    S = set()
    T = set()
    for query_image in truthmap:
        truth_res = truthmap[query_image]
        mission_res = missionmap[query_image]
        # compute the worst case senario, where Z = empty
        maxError = ((1 + len(truth_res)) * len(truth_res) / 2) * 2
        # setup S and T
        S.update(truth_res)
        T.update(mission_res)
        Z = S & T #Z includes images both in S and T
        # clear S and T
        for s in Z:
            T.remove(s)
            S.remove(s)
        # now that Z, S, and T are set, compute the ranking function
        ranking_res = compute2(truth_res, mission_res, Z) - compute1(truth_res, S) - compute1(mission_res, T)
        ranking_res = abs(float(ranking_res) / float(maxError))
        # normalize the error
        qos_report.write(query_image)
        qos_report.write("S"+str(len(S)) + "  Z" + str(len(Z)) + " T"+str(len(T)) + "  ")
        qos_report.write(str(compute2(truth_res, mission_res, Z)) + "  "+ str(compute1(truth_res, S)) + "  "+ str(compute1(mission_res, T)))
        qos_report.write("\t")
        qos_report.write(str(ranking_res) + "\n")
        S.clear()
        T.clear()
        Z.clear()
    qos_report.close()

def rank(img, imglist):
    if img in imglist:
        return imglist.index(img)+1
    return 0

def compute1(list1, imgset):
    res = 0
    for img in imgset:
        res += rank(img,list1)
    return res

def compute2(list1, list2, imgset):
    res = 0
    for img in imgset:
        res += abs(rank(img,list1) - rank(img, list2))
    return res


#QOS checker for Swaptions
def checkSwaption(fact, observed):
    print "Im here"
    truth = open(fact, "r")
    mission = open(observed, "r")
    qos_report = open("qos_report", "w")
    truth_map = {}
    mission_map = {}
    totalRound = 0
    for line in truth:
        col = line.split(':')
        round_num = col[0]
        round_res = float(col[1].split(',')[0])
        truth_map[round_num] = round_res
        totalRound += 1
    for line in mission:
        col = line.split(':')
        round_num = col[0]
        round_res = float(col[1].split(',')[0])
        mission_map[round_num] = round_res
    # calculate the distortion
    for round in range(0,totalRound):
        roundname = "round"+str(round)
        truth_res = truth_map[roundname]
        mission_res = mission_map[roundname]
        error = abs((truth_res - mission_res)/truth_res)
        qos_report.write(roundname)
        qos_report.write("\t")
        qos_report.write(str(error))
        qos_report.write("\n")
    # close the report
    qos_report.close()
