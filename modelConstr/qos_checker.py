"""QOS loss checker for all apps"""
import numpy

knob_ferret_itr = numpy.linspace(1, 25, num=25)
knob_ferret_hash = numpy.linspace(2, 8, num=4)
knob_ferret_probe = numpy.linspace(2, 20, num=10)

knob_bodytrack = numpy.linspace(100, 4000, num=40)
knob_bodytrack_annealing = [1, 2, 3, 4, 5]

def checkFerretWrapper(fact, observed=""):
    name = "output_";
    report = open("finalReport", 'w')
    if (observed == ""):
        for i in range(0, len(knob_ferret_hash)):  # run the application for each configuratino
            for j in range(0, len(knob_ferret_probe)):
                for k in range(0, len(knob_ferret_itr)):
                    cur_name = name + str(int(knob_ferret_hash[i]))
                    cur_name += "_" + str(int(knob_ferret_probe[j]))
                    cur_name += "_" + str(int(knob_ferret_itr[k]))
                    report.write(cur_name)
                    report.write(",")
                    cur_name += ".txt"
                    checkFerret(fact, cur_name, report)
                    report.write("\n")
    else:
        checkFerret(fact, observed, report)
    report.close()

#QOS checker for ferret
def checkFerret(fact, observed, report):
    truth = open(fact, "r")
    mission = open(observed, "r")
    truthmap = {}
    missionmap = {}
    truth_res = []
    mission_res = []
    qos_report = open("qos_report", "w")
    for line in truth:
        col = line.split('\t')
        name = col[0].split("/")[1]
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
    toterr = 0.0
    totimg = 0
    for query_image in truthmap:
        totimg += 1
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
        toterr += 1.0-ranking_res
        S.clear()
        T.clear()
        Z.clear()
    qos_report.close()
    report.write(str(toterr/totimg))

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

def checkSwaptionWrapper(fact, observed=""):
    name = "output_";
    report = open("finalReport",'w')
    if(observed == ""):
        for i in range(100000, 1100000, 100000):
            cur_name = name + str(i)
            cur_name += ".txt"
            checkSwaption(fact, cur_name, report)
    else:
        checkSwaption(fact, observed, report)
    report.close()

#QOS checker for Swaptions
def checkSwaption(fact, observed,report):
    truth = open(fact, "r")
    mission = open(observed, "r")
    qos_report = open(observed+"_qos_report", "w")
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
    toterr = 0.0
    for round in range(0,totalRound):
        roundname = "round"+str(round)
        truth_res = truth_map[roundname]
        mission_res = mission_map[roundname]
        error = abs((truth_res - mission_res)/truth_res)
        qos_report.write(roundname)
        qos_report.write("\t")
        qos_report.write(str(error))
        qos_report.write("\n")
        toterr += error
    # write the average error
    meanQoS = 1 - toterr / totalRound
    #errfile = open("qos", "w")
    #errfile.write(str(1 - toterr/totalRound))
    #errfile.close()
    qos_report.write(str(meanQoS) + "\n")
    # close the report
    qos_report.close()
    # write to final total
    report.write(str(meanQoS) + "\n")

def checkBodytrackWrapper(fact, observed=""):
    name = "output_";
    report = open("finalReport",'w')
    if (observed == ""):
        for i in range(0, len(knob_bodytrack)):  # run the application for each configuratino
            for j in range(0, len(knob_bodytrack_annealing)):
                cur_name = name + str(int(knob_bodytrack[i]))
                cur_name += "_" + str(int(knob_bodytrack_annealing[j]))
                report.write(cur_name)
                report.write(",")
                cur_name += ".txt"
                checkBodytrack(fact, cur_name, report)
                report.write("\n")
    else:
        checkBodytrack(fact, observed, report)
    report.close()

weight = [0.01, 0.01, 0.1, 100,100,100, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 1, 0.01, 0.1, 0.1, 1, 0.1, 1, 0.1, 0.1, 0.1,
10, 0.1, 1, 0.1, 0.1, 0.01, 0.01, 0.1, 0.01, 0.1]

#QOS checker for Bodytrack
def checkBodytrack(fact, observed, report):
    truth = open(fact, "r")
    mission = open(observed, "r")
    qos_report = open(observed + ".report", "w")
    totalRound = 0
    truth_results = []
    mission_results = []
    for line in truth:
        round_res = line.split()
        truth_results.append(round_res)
    for line in mission:
        round_res = line.split()
        mission_results.append(round_res)
    totDistortion = 0.0
    for i in range(0, len(truth_results)):
        # truth_results[i] is a vector, compute the vector distortion
        distortion = 0.0
        for j in range (0, len(truth_results[i])):
            if(truth_results[i][j]=="\n"):
                continue
            curtrue = float(truth_results[i][j])
            curmission = float(mission_results[i][j])
            distortion += abs(weight[j]/10*(curtrue - curmission) / curtrue)
        distortion /= len(truth_results[i])
        qos_report.write("frame")
        qos_report.write(str(i))
        qos_report.write(":")
        qos_report.write(str(distortion))
        qos_report.write("\n")
        totDistortion += distortion
    qos_report.close()
    report.write(str(totDistortion / len(truth_results)))
