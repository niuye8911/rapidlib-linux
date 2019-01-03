import json
import os

database_path = "/home/liuliu/Research/mara_bench/parsec-3.0/pkgs/apps/ferret" \
                "/run/corelnative/"
table = "lsh"
query_path = "/home/liuliu/Research/mara_bench/parsec-3.0/pkgs/apps/ferret" \
             "/run/queriesnative"

obj_path = '/home/liuliu/Research/mara_bench/parsec-3.0/pkgs/apps/ferret/inst' \
           '/amd64-linux.gcc-serial/bin/ferret'


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


def getQoS(missionfile):
    truth = open('./output_ground.txt', "r")
    mission = open(missionfile, "r")
    truthmap = {}
    missionmap = {}
    truth_res = []
    mission_res = []
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
        coverage = -2 * (len(truth_res) - len(Z)) * (
                    len(truth_res) + 1) / float(maxError)
        ranking = -1 * (
                    compute2(truth_res, mission_res, Z) - compute1(truth_res,
                                                                   S) -
                    compute1(
                mission_res, T)) / float(maxError)
        ranking_res = (1.0 + coverage + ranking) * 100.0

        # convert coverage to Z
        coverage = len(Z) / len(truth_res)
        totAcuracy += ranking_res
        totRanking += ranking
        totCoverage += coverage
        S.clear()
        T.clear()
        Z.clear()
    print[totCoverage / float(totimg),
          totRanking / float(totimg),
          totAcuracy / float(totimg)]


def run(preferences):
    # generate the xml
    cmd = ['python',
           config['rapidScript'],
           '--cfg',
           './ferret_run.config',
           "--model",
           "piecewise",
           "-m",
           "finalize",
           ]
    os.system(" ".join(cmd))
    # run ferret
    output_name = "custom_outputs/output" + "_" + str(
        preferences[0]) + "_" + str(preferences[1]) + ".txt"
    ferret_cmd = [obj_path,
                  database_path,
                  table, query_path,
                  "50",
                  "20",
                  "1",
                  output_name,
                  '-rsdg',
                  '-cont',
                  '-xml',
                  './outputs/ferret.xml',
                  '-b',
                  '125',
                  '-u',
                  '100'
                  ]
    print(' '.join(ferret_cmd))
    os.system(' '.join(ferret_cmd))

    # check the result
    getQoS(output_name)
    # move the xml
    mv_cmd = ['mv',
              './outputs/ferret.xml',
              './xmls/ferret' + "_" + str(preferences[0]) + "_" + str(
                  preferences[1]) + ".xml"]
    os.system(" ".join(mv_cmd))


with open('./ferret_run.config', 'r') as config_json:
    config = json.load(config_json)

for preferences in range(1, 10):
    # relavance from 1 to 10
    config['preferences'][1] = float(1.0 + 0.1 * float(preferences))
    configfile = open('./ferret_run.config', 'w')
    json.dump(config, configfile, indent=2, sort_keys=True)
    configfile.close()
    run(config['preferences'])
