import optparse

from LP_Util.merge import *
from qos_checker import *
from contigous import *
import numpy as np

configs = []
service_levels = {}
observed = ""
fact = ""
KF = ""
app = ""
targetMax = 0.05 
targetMean = 0.02

# return a map where each entry is the service name and the value is the total number of levels
def parseDetail(fileName):
    f = open(fileName,'r')
    res = {}
    for line in f:
        col = line.split()
        name = col[0]
        lvl = col[1]
        res[name] = int(lvl)
    return res

def checkRate(rsdg,fact,target):
    factCost = open(fact,'r')
    report = open("report",'w')
    meanErr = 0.0
    maxErr = 0.0
    maxId = -1
    TotErr = 0.0
    TotConfig = 0
    lineNum = 0
    outlier = []
    for line in factCost:
        lineNum+=1
        col = line.split(',')
        length = len(col)
        name = ""
        lvl = -1
        gtV = -1
        estV = 0
        TotConfig += 1
        for i in range(0, length):
            if i == length - 1:
                gtV = float(col[i])
                err = abs((gtV-estV)/gtV)
                report.write("%f,%f,err:%f\n" % (gtV , estV, err))
                TotErr += err
                if err >= target : outlier.append(line)
                if err >= maxErr : maxId = lineNum
                maxErr = max(maxErr,err)
                TotConfig += 1
                estV = 0
                continue
            cur = col[i]
            # write the current element to file
            report.write(cur)
            report.write(",")
            if not (cur.isdigit()):  # if it's service name
                name = cur
            else:
                lvl = int(cur)
                if not (lvl == 0):
                    estV += rsdg[name][lvl-1]
                else:
                    estV += rsdg[name][0]
    meanErr = TotErr/TotConfig
    report.write("Mean:"+str(meanErr))
    report.close()
    return [meanErr,maxErr, maxId, outlier]

# populate a fully blown RSDG with observed measurement
def populateRSDG(observedFile, factFile, cont):
    if cont == True:
        paras = genContProblem(factFile)
        os.system("gurobi_cl ResultFile=max.sol contproblem.lp")
        getContRSDG(paras)
        return

    global configs, service_levels
    # setup the configuration
    configs, service_levels = generateConfigsFromTraining(factFile)
    observed_configs, dummy = generateConfigsFromTraining(observedFile)
    if cont==False:#if it's a discrete
        genProblem(service_levels, observed_configs)
    rsdg = solveAndPopulate(service_levels, True)
    [meanErr, maxErr, maxId, dummy] = checkRate(rsdg, fact, targetMax)
    print "Mean:" + str(meanErr) + "\tMax:" + str(maxErr)
    print "maxConfig:" + str(maxId)

def genRS(fact):
    global configs, service_levels
    represented_set = []
    selected = {} # selected configurations id in RS
    curConfigs = [] # selected configurations in RS
    # get the configs from the file
    configs, service_levels = generateConfigsFromTraining(fact)
    totalNumOfConfigs = len(configs)

    #add the top and last config
    curConfigs.append(configs[0])
    curConfigs.append(configs[totalNumOfConfigs-1])

    represented_set.append(configs[0])
    represented_set.append(configs[totalNumOfConfigs-1])

    selected[0] = True
    selected[totalNumOfConfigs-1] = True

    #iterate through all constraints
    curMeanErr = 10.0
    curMaxErr = 10.0
    smallest = -1
    while smallest!=-2 and(curMeanErr>=targetMean or curMaxErr>=targetMax):#target mean err
    #for x in range(0,20):
        smallest = -2
        biggestinsmallest = -2
        maxErrTmp = 10.0
        outlier = []
        for i in range(1,totalNumOfConfigs-1):
            if(selected.has_key(i)):continue # if already in the list
            #add the new config to the RS
            curConfigs.append(configs[i])
            # generate the optimization problem
            genProblem(service_levels, curConfigs)
            # fetch the resulting rsdg
            rsdg = solveAndPopulate(service_levels, False)
            [meanErr,maxErr, maxId,out] = checkRate(rsdg,fact, targetMax)
            if(meanErr <= maxErrTmp):
                maxErrTmp = meanErr
                curMeanErr = meanErr
                curMaxErr = maxErr
                smallest = i
                biggestinsmallest = maxId
                outlier = out
            # pop out the newly added config
            curConfigs.pop()
        # add the one config that is the smallest into the
        selected[smallest] = True
        #selected[biggestinsmallest] = True
        print "Mean:"+str(curMeanErr)+"\tMax:"+str(curMaxErr)+"\tselected:"+str(smallest) + "/"+str(biggestinsmallest)
        print "maxConfig:"+str(maxId)
        represented_set.append(configs[smallest])

        curSmallest, curSmallest_dual = genConstraintFromConfig(configs[smallest])
        curConfigs.append(configs[smallest])

    #generate the final problem
    genProblem(service_levels, curConfigs)
    rsdg = solveAndPopulate(service_levels, True)
    checkRate(rsdg, fact, targetMax)

    #write result to a file
    resFile = open("RS",'w')
    for eachConfig in represented_set:
        resFile.write(eachConfig.print_yourself())
        resFile.write("\n")
    return represented_set

def checkAccuracy():
    global fact, app, observed
    if app=="ferret":
        checkFerretWrapper(fact, observed)
    elif app == "swaptions":
        checkSwaptionWrapper(fact, observed)
    elif app == "bodytrack":
        checkBodytrackWrapper(fact, observed)


def polyfit():
    x = np.array([100000, 200000, 300000, 400000, 500000, 600000, 700000, 800000, 900000, 1000000])
    y = np.array([1393, 2777, 4161, 5545, 6929, 8313, 9697, 11081, 12412, 13863])
    func = np.polyfit(x, y, 2)
    func
    return func


def main(argv):
    global config, observed, fact, KF, app

    #parse the argument
    parser = optparse.OptionParser()
    parser.add_option('-f', dest="fact")
    parser.add_option('-k', dest="KF")
    parser.add_option('--k1', dest="KF1")
    parser.add_option('--k2', dest="KF2")
    parser.add_option('-m', dest="mode", default="checkRate")
    parser.add_option('-o', dest="observed")
    parser.add_option('--r1', dest="r1")
    parser.add_option('--r2', dest='r2')
    parser.add_option('-a', dest='app')

    options, args = parser.parse_args()
    observed = options.observed
    fact = options.fact
    KF = options.KF
    KF1 = options.KF1
    KF2 = options.KF2
    app = options.app
    mode = options.mode

    if(mode=="genrs"):
        genRS(fact)
        return 0

    if(mode=="merge"):
        r1 = getRSDG(options.r1)
        r2 = getRSDG(options.r2)
        genNewProblem(r1, r2, observed,KF1,KF2)
        rsdgMerge = genNewRSDG(r1,r2)
        [meanErr, maxErr, maxId, out]=checkRate(rsdgMerge, fact, targetMax)
        print meanErr
        print maxErr
        print maxId
        print len(out)

        return 0

    if (mode == "nmerge"):
        r1 = getRSDG(options.r1)
        r2 = getRSDG(options.r2)
        rsdgMerge = naiveMerge(r1, r2)
        [meanErr, maxErr, maxId, out] = checkRate(rsdgMerge, fact, targetMax)
        printRSDG(rsdgMerge,False)
        return 0

    if (mode == "consrsdg"):# construct RSDG based on observation of RS
        populateRSDG(observed, fact, False)
        return 0

    if (mode == "conscontrsdg"):# construct RSDG based on observation of RS
        populateRSDG(observed, fact, True)
        return 0

    if (mode == "qos"): #check the QoS loss of two different runtime behavior
        # fact will be the golden truth
        # observed will be the actual runtime data
        checkAccuracy()
        return 0

    if (mode == "polyfit"):
        polyfit()
        return 0

    #read known fact
    kf = parseKF(KF)
    #print problem
    """genProblem(res,obs,kf)
    #solve problem and populate RSDG
    rsdg = getResult(res,True)
    #check rate
    [meanErr, maxErr, maxId, out]=checkRate(rsdg,fact,targetMax)
    print meanErr
    print maxErr
    print maxId
    print out"""

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))





