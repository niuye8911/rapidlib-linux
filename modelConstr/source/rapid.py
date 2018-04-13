import optparse
from LP_Util.merge import *
from representset import *
from xmlgen import *
from stage_1.training import *
from Parsing_Util.readFact import *
from representList import *
from Classes import  *

configs = []
service_levels = {}
observed = ""
fact = ""
KF = ""
app = ""
model = "quad"
rs = "set"
remote = False
targetMax = 0.05 
targetMean = 0.02
groundTruth_profile = Profile()
knobs = {}
knob_samples = {}
desc = ""
stage = -1

THRESHOLD = 0.05

def main(argv):
    #parse the argument
    parser = declareParser()
    options, args = parser.parse_args()
    # insert to global variables
    parseCMD(options)

    # declare a output path
    if not os.path.exists("./outputs"):
        os.system("mkdir outputs")

    #######################STAGE-1########################
    #generate training set
    if desc=="":
        print "required a description of program with option --desc"
        return
    global groundTruth_profile, knob_samples, knobs
    knobs,groundTruth_profile, knob_samples = genTrainingSet(desc)

    # generate XML files
    #genxml(options.rsdg,options.rsdgmv,True,options.dep)
    genxml("","",True,desc)
    if (stage == 1):
        return

    #######################STAGE-2########################
    #second stage: Binding, nothing to be done here, all done in source

    #######################STAGE-3########################
    #third stage: Training, the source library will take care of the training, the output is a fact.csv file

    #######################STAGE-4########################
    #forth stage, explore the trained profile and generate representative list
    # read in the trained profile, the profile key is a string representing the configuration, value is the cost
    readFact("fact.csv",knobs,groundTruth_profile)
    groundTruth_profile.printProfile("profile.csv")
    # construct the RL iteratively given a threshold
    genRL(groundTruth_profile,knob_samples, THRESHOLD)
    if (stage == 4):
        return

    if(mode=="genrs"):
        if (rs=="set"):
            genRS(fact,True,targetMax,targetMean)
        else:
            genRS(fact,False,targetMax,targetMean)
        return 0

    if (mode == "consrsdg"):# construct RSDG based on observation of RS
        populateRSDG(observed, fact, False, "linear", remote)
        return 0

    if (mode == "conscontrsdg"):# construct RSDG based on observation of RS
        populateRSDG(observed, fact, True, model,remote)
        return 0

    if (mode == "qos"): #check the QoS loss of two different runtime behavior
        # fact will be the golden truth
        # observed will be the actual runtime data
        checkAccuracy()
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

    return 0

def declareParser():
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
    parser.add_option('-r', dest='remote')
    parser.add_option('--model', dest="model")
    parser.add_option('--rs', dest="rs")
    parser.add_option('--rsdg', dest="rsdg")
    parser.add_option('--rsdgmv', dest="rsdgmv")
    parser.add_option('--dep', dest="dep")
    parser.add_option('--desc', dest="desc")
    parser.add_option('--stage', dest='stage')
    return parser

def parseCMD(options):
    global config, observed, fact, KF, app, remote, model, rs,desc,stage,mode
    observed = options.observed
    fact = options.fact
    KF = options.KF
    KF1 = options.KF1
    KF2 = options.KF2
    app = options.app
    model = options.model
    rs = options.rs
    remote = options.remote
    mode = options.mode
    desc = options.desc
    stage = int(options.stage)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

