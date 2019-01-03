"""QOS loss checker for all apps"""
import numpy

knob_ferret_itr = numpy.linspace(1, 25, num=25)
knob_ferret_hash = numpy.linspace(2, 8, num=4)
knob_ferret_probe = numpy.linspace(2, 20, num=10)

knob_bodytrack = numpy.linspace(100, 4000, num=40)
knob_bodytrack_annealing = [1, 2, 3, 4, 5]

weight = [160.000000000000, 160.000000000000, 0.883801457794, 1.000000000000,
          90.000000000000, 80.000000000000,
          1.000000000000, 1.000000000000, 80.000000000000, 80.000000000000,
          1.000000000000, 1.000000000000,
          90.000000000000, 80.000000000000, 1.000000000000, 1.000000000000,
          80.000000000000, 80.000000000000,
          1.000000000000, 1.000000000000, 60.000000000000, 40.000000000000,
          1.000000000000, 1.000000000000,
          40.000000000000, 30.000000000000, 1.000000000000, 1.000000000000,
          60.000000000000, 40.000000000000,
          1.000000000000, 1.000000000000, 40.000000000000, 30.000000000000,
          1.000000000000, 1.000000000000,
          108.219779804448, 108.219779804448,
          1.000000000000, 0.739581901676, 578.571268037074, 98.775717746183,
          424.775528050607, 449.138638864995,
          0.000000000000, 112.973551984717, 393.591975105289, 464.725142771880,
          0.000000000000, 241.301534024968,
          205.666008552084,
          220.311272548189, 0.000000000000, 176.865773690142, 243.325288891550,
          247.925686687300, 0.000000000000,
          268.030179506415]


def checkFerretWrapper(fact, observed=""):
    name = "output_";
    report = open("finalReport", 'w')
    if (observed == ""):
        for i in range(0, len(
                knob_ferret_hash)):  # run the application for each
            # configuratino
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


# QOS checker for ferret
def checkFerret(fact, observed, REPORT, report=""):
    truth = open(fact, "r")
    mission = open(observed, "r")
    truthmap = {}
    missionmap = {}
    truth_res = []
    mission_res = []
    qos_report = open("qos_report", "w")
    for line in mission:
        col = line.split('\t')
        name = col[0].split("/")[1]
        missionmap[name] = []
        for i in range(1, len(col)):  # 50 results
            missionmap[name].append(col[i].split(':')[0])
    for line in truth:
        col = line.split('\t')
        name = col[0].split("/")[1]
        if not name in missionmap:
            continue
        truthmap[name] = []
        for i in range(1, len(col)):  # 50 results
            truthmap[name].append(col[i].split(':')[0])
    print
    len(truthmap)
    print
    len(missionmap)
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
        Z = S & T  # Z includes images both in S and T
        # clear S and T
        for s in Z:
            T.remove(s)
            S.remove(s)
        # now that Z, S, and T are set, compute the ranking function
        ranking_res = compute2(truth_res, mission_res, Z) - compute1(truth_res,
                                                                     S) - \
                      compute1(
            mission_res, T)
        ranking_res = abs(float(ranking_res) / float(maxError))
        # normalize the error
        if REPORT:
            qos_report.write(query_image)
            qos_report.write(
                "S" + str(len(S)) + "  Z" + str(len(Z)) + " T" + str(
                    len(T)) + "  ")
            qos_report.write(
                str(compute2(truth_res, mission_res, Z)) + "  " + str(
                    compute1(truth_res, S)) + "  " + str(
                    compute1(mission_res, T)))
            qos_report.write("\t")
            qos_report.write(str(ranking_res) + "\n")
        toterr += 1.0 - ranking_res
        S.clear()
        T.clear()
        Z.clear()
    print(str(toterr / totimg * 100.0))
    if REPORT:
        qos_report.close()
    if not REPORT:
        report.write(str(toterr / totimg * 100.0))


def rank(img, imglist):
    if img in imglist:
        return imglist.index(img) + 1
    return 0


def compute1(list1, imgset):
    res = 0
    for img in imgset:
        res += rank(img, list1)
    return res


def compute2(list1, list2, imgset):
    res = 0
    for img in imgset:
        res += abs(rank(img, list1) - rank(img, list2))
    return res


def checkSwaptionWrapper(fact, observed=""):
    name = "output_";
    report = open("finalReport", 'w')
    if (observed == ""):
        for i in range(100000, 1100000, 100000):
            cur_name = name + str(i)
            cur_name += ".txt"
            checkSwaption(fact, cur_name, report)
    else:
        checkSwaption(fact, observed, report)
    report.close()


# QOS checker for Swaptions
def checkSwaption(fact, observed, REPORT, report=""):
    truth = open(fact, "r")
    mission = open(observed, "r")
    if REPORT:
        qos_report = open(observed + ".report", "w")
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
    for round in range(0, totalRound):
        roundname = "round" + str(round)
        truth_res = truth_map[roundname]
        mission_res = mission_map[roundname]
        error = abs((truth_res - mission_res) / truth_res)
        # print roundname, truth_res, mission_res, truth_res - mission_res,error
        if REPORT:
            qos_report.write(roundname)
            qos_report.write("\t")
            qos_report.write(str(error))
            qos_report.write("\n")
        toterr += error
    # write the average error
    meanQoS = 1 - toterr / totalRound
    meanQoS = meanQoS * 1000.0 - 999
    if REPORT:
        qos_report.write(str(meanQoS) + "\n")
        # close the report
        qos_report.close()
    # write to final total
    if not REPORT:
        report.write(str(meanQoS * 100.0))


def checkBodytrackWrapper(fact_path, observed_path):
    name = "output_";
    report = open("finalReport", 'w')
    for i in range(0, len(
            knob_bodytrack)):  # run the application for each configuratino
        for j in range(0, len(knob_bodytrack_annealing)):
            cur_name = name + str(int(knob_bodytrack[i]))
            cur_name += "_" + str(int(knob_bodytrack_annealing[j]))
            report.write(cur_name)
            report.write(",")
            cur_name += ".txt"
            checkBodytrack(fact_path, cur_name, report)
            report.write("\n")
    else:
        checkBodytrack(fact_path, observed_path, report)
    report.close()


weight1 = [0.01, 0.01, 0.1, 10, 10, 10, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 1, 0.01,
           0.1, 0.1, 1, 0.1, 1, 0.1, 0.1, 0.1, 10,
           0.1, 1, 0.1, 0.1, 0.01, 0.01, 0.1, 0.01, 0.1]

# #weight1=[0.011338610057,
# 0.005919741171,
# 0.057843614221,
# 13.727886981200,
# 17.187018644850,
# 2.379470311382,
# 0.022951360510,
# 0.044646538338,
# 0.036911865600,
# 0.092811089369,
# 0.045403438045,
# 0.039861916358,
# 0.047238494363,
# 0.075382591595,
# 0.003043376268,
# 0.005335630451,
# 0.016916489037,
# 0.029655329941,
# 0.035955264466,
# 0.051108968665,
# 0.004577192249,
# 0.004803275130,
# 0.015447161151,
# 0.039358547774,
# 0.056909245307,
# 0.045386111756,
# 0.008205836377,
# 0.033335148872,
# 0.013288913439,
# 0.011086279806,
# 0.034133414639,
# -0.205444856555,
# -0.041174863964,
# -100000.000000000000,
# -100000.000000000000,
# -100000.000000000000,
# 837.979505097739,
# -0.165579658090,
# -0.521959260503,
# -0.406563037410,
# -1.443430612060,
# -0.324637147706,
# -0.462231279257,
# -0.766701903642,
# -1.213189691668,
# 0.143656577776,
# -0.094380855544,
# 0.107255649197,
# -2.002108561475,
# -0.700022865039,
# -1.591114845451,
# -0.156531883623,
# -0.203554423123,
# 0.049774887548,
# 0.925640387672,
# 2.467495026767,
# -1.245737733588,
# -0.208051753577,
# -0.377472100128,
# -0.195977648371,
# -0.736709235490,
# -0.829305494724,
# 0.203088373877,
# 0.192291975825,
# 100000.000000000000,
# 100000.000000000000,
# 100000.000000000000,
# 919.851897180395,
# 0.312356055276,
# 0.702874953670,
# 0.452157995184,
# 0.470077368405,
# 0.317614914595,
# 0.556567911331,
# 0.013347875116,
# 0.403964962535,
# 0.266389672856,
# 0.057129198835,
# 0.500852171391,
# -0.979710402176,
# 0.349217179266,
# -0.173866100549,
# -0.065664400279,
# -0.077682063480,
# 0.387208249277,
# 2.272992980587,
# 3.835035160915,
# -0.140357427174,
# 0.025953796640,
# 0.402589406454,
# 0.551102596995,
# -0.035442534363,
# 1.026253619371]

norm_weight = sum(weight)


# QOS checker for Bodytrack
def checkBodytrack(fact, observed, REPORT, report):
    print(len(weight))
    truth = open(fact, "r")
    mission = open(observed, "r")
    qos_report = open("report", "w")
    if REPORT:
        print
        "creating report"
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
        for j in range(0, len(truth_results[i])):
            if (truth_results[i][j] == "\n"):
                continue
            curtrue = float(truth_results[i][j])
            curmission = float(mission_results[i][j])
            val = abs((curtrue - curmission) / curtrue)
            print
            curtrue, curmission, val
            if val > 1:
                val = 1
            distortion += val
        distortion /= len(truth_results[i])
        print
        distortion
        if REPORT:
            qos_report.write("frame")
            qos_report.write(str(i))
            qos_report.write(":")
            qos_report.write(str(distortion))
            qos_report.write("\n")
        totDistortion += distortion
    print(1.0 - (totDistortion / len(truth_results))) * 100.0
    if not REPORT:
        report.write(str((1.0 - (totDistortion / len(truth_results))) * 100.0))
    if REPORT:
        qos_report.write(
            str((1.0 - (totDistortion / len(truth_results))) * 100.0))
        qos_report.close()
