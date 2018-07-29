import optparse
from LP_Util.merge import *
from xmlgen import *
from Parsing_Util.readFact import *
from stage_1.training import *
from stage_2.trainApp import *
from stage_4.constructRSDG import *
from Classes import  *
from representset import populateRSDG, genRS
from plot import *
from stage_2.qos_checker import *
import imp

configs = []
service_levels = {}
observed = ""
fact = ""
KF = ""
app = ""
model = "quad"
rs = "set"
remote = False
targetMax = 0.1
targetMean = 0.05
groundTruth_profile = Profile()
knobs = Knobs()
knob_samples = {}
desc = ""
stage = -1
methods_path = ""
PLOT=False

THRESHOLD = 0.05

def main(argv):
    #parse the argument
    parser = declareParser()
    options, args = parser.parse_args()
    # insert to global variables
    parseCMD(options)

    # make the output dirs
    if not os.path.exists("./outputs"):
        os.system("mkdir outputs")
    if not os.path.exists("./debug"):
        os.system("mkdir debug")
    if not os.path.exists("./training_outputs"):
        os.system("mkdir training_outputs")

    #######################STAGE-1########################
    #generate initial training set
    if desc=="":
        print "required a description of program with option --desc"
        return
    global groundTruth_profile, knob_samples, knobs
    appname,knobs,groundTruth_profile, knob_samples,and_edges,or_edges,knob_list = genTrainingSet(desc)
    appname = appname[:-1]
    # generate XML files
    xml = genHybridXML(appname, and_edges, or_edges, knob_list)
    if (stage == 1):
        return

    #######################STAGE-2########################
    #second stage: Training, the source library will take care of the training, the output is a bodytrack.fact file
    # load user-supplied methods
    module = imp.load_source("", methods_path)
    appMethods = module.appMethods(appname)
    factfile, mvfactfile = genFact(appname,groundTruth_profile,appMethods)
    if (stage == 2):
        return

    #######################STAGE-3########################
    #third stage: Modeling, use the specific modeling method to construct the RSDG
    readFact(factfile, knobs, groundTruth_profile)
    readFact(mvfactfile, knobs, groundTruth_profile, False)
    groundTruth_profile.printProfile("./outputs/" + appname + ".profile")
    # construct the cost rsdg iteratively given a threshold
    cost_rsdg, mv_rsdg = constructRSDG(groundTruth_profile, knob_samples, THRESHOLD, knobs, True, model)
    if PLOT:
        draw("outputs/modelValid.csv")

    #######################STAGE-4########################
    #forth stage, generate the final RSDG in XML format
    completeXML(appname,xml,cost_rsdg,mv_rsdg,model)

    # cleaning
    os.system("rm *.log *.sol")
    if (stage == 4):
        return

#######SOME EXTRA MODES#############

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

    if (mode == "genrs"):
        if (rs == "set"):
            genRS(fact, True, targetMax, targetMean)
        else:
            genRS(fact, False, targetMax, targetMean)
        return 0

    if (mode == "consrsdg"):  # construct RSDG based on observation of RS
        populateRSDG(observed, fact, False, "linear", remote)
        return 0

    if (mode == "conscontrsdg"):  # construct RSDG based on observation of RS
        # get an observed file by randomly select some observation
        populateRSDG(observed, fact, True, model, remote)
        return 0

    if (mode == "qos"):  # check the QoS loss of two different runtime behavior
        # fact will be the golden truth
        # observed will be the actual runtime data
        if app == "swaptions":
            checkSwaption(fact, observed, True, "")
        if app == "ferret":
            checkFerret(fact, observed, True, "")
        if app == "bodytrack":
            checkBodytrack(fact, observed, True, "")
        return

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
    parser.add_option("-p",dest="plot")
    parser.add_option('--rs', dest="rs")
    parser.add_option('--rsdg', dest="rsdg")
    parser.add_option('--rsdgmv', dest="rsdgmv")
    parser.add_option('--dep', dest="dep")
    parser.add_option('--desc', dest="desc")
    parser.add_option('--stage', dest='stage')
    parser.add_option('--met', dest='method')
    return parser

def parseCMD(options):
    global config, observed, fact, KF, app, remote, model, rs,desc,stage,methods_path,mode,PLOT
    observed = options.observed
    fact = options.fact
    KF = options.KF
    KF1 = options.KF1
    KF2 = options.KF2
    app = options.app
    model = options.model
    if options.plot=="t":
        PLOT=True
    rs = options.rs
    remote = options.remote
    mode = options.mode
    desc = options.desc
    if not options.stage == None:
        stage = int(options.stage)
    if not options.method == None:
        methods_path = options.method
    else:
        print("expected user supplied app methods")
	if not (stage == 1):
		exit(1)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
