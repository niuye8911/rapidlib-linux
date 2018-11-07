import imp
import json
import optparse

from LP_Util.merge import *
from Parsing_Util.readFact import *
from plot import *
from representset import populateRSDG, genRS
from stage_1.training import *
from stage_2.qos_checker import *
from stage_2.trainApp import *
from stage_4.constructRSDG import *
from xmlgen import *

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
obj_path = ""
config_file = ""
app_config = None
PLOT = False

withSys = True
withQoS = False
withPerf = True

THRESHOLD = 0.05


def main(argv):
    # parse the argument
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
    # generate initial training set
    if desc == "":
        print
        "required a description of program with option --desc"
        return
    global groundTruth_profile, knob_samples, knobs
    appname, knobs, groundTruth_profile, knob_samples = genTrainingSet(desc)
    appname = appname[:-1]

    # generate XML files
    xml = genxml(appname, "", "", True, desc)
    if (stage == 1):
        return

    #######################STAGE-2########################
    # second stage: Training, the source library will take care of the training, the output is a bodytrack.fact file
    # load user-supplied methods
    module = imp.load_source("", methods_path)
    appMethods = module.appMethods(appname, obj_path)
    factfile, mvfactfile = genFact(appname, groundTruth_profile, appMethods, withQoS, withSys, withPerf)

    #######################STAGE-3########################
    # third stage: Modeling, use the specific modeling method to construct the RSDG
    readFact(factfile, knobs, groundTruth_profile)
    readFact(mvfactfile, knobs, groundTruth_profile, False)
    groundTruth_profile.printProfile("./outputs/" + appname + ".profile")
    # construct the cost rsdg iteratively given a threshold
    cost_rsdg, mv_rsdg = constructRSDG(groundTruth_profile, knob_samples, THRESHOLD, knobs, True, model)
    if PLOT:
        draw("outputs/modelValid.csv")

    #######################STAGE-4########################
    # forth stage, generate the final RSDG in XML format
    completeXML(appname, xml, cost_rsdg, mv_rsdg, model)

    # cleaning
    os.system("rm *.log *.sol")
    if (stage == 4):
        return

    #######SOME EXTRA MODES#############

    if (mode == "merge"):
        r1 = getRSDG(options.r1)
        r2 = getRSDG(options.r2)
        genNewProblem(r1, r2, observed, KF1, KF2)
        rsdgMerge = genNewRSDG(r1, r2)
        [meanErr, maxErr, maxId, out] = checkRate(rsdgMerge, fact, targetMax)
        print
        meanErr
        print
        maxErr
        print
        maxId
        print
        len(out)

        return 0

    if (mode == "nmerge"):
        r1 = getRSDG(options.r1)
        r2 = getRSDG(options.r2)
        rsdgMerge = naiveMerge(r1, r2)
        [meanErr, maxErr, maxId, out] = checkRate(rsdgMerge, fact, targetMax)
        printRSDG(rsdgMerge, False)
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
    parser.add_option('-r', dest='remote')
    parser.add_option('--model', dest="model")
    parser.add_option("-p", dest="plot")
    parser.add_option('--rs', dest="rs")
    parser.add_option('--rsdg', dest="rsdg")
    parser.add_option('--rsdgmv', dest="rsdgmv")
    parser.add_option('--stage', dest='stage')
    parser.add_option('-C', dest="config")
    return parser


def parseCMD(options):
    global app_config, observed, fact, KF, remote, model, rs, stage, mode, PLOT, config_file
    observed = options.observed
    fact = options.fact
    KF = options.KF
    KF1 = options.KF1
    KF2 = options.KF2
    model = options.model
    if options.plot == "t":
        PLOT = True
    rs = options.rs
    remote = options.remote
    mode = options.mode
    # read config
    if not options.config == None:
        config_file = options.config
        app_config = parseConfig(config_file)
    if not options.stage == None:
        stage = int(options.stage)


def parseConfig(config_file):
    global desc, methods_path, obj_path
    with open(config_file) as config_json:
        config = json.load(config_json)
        desc = config['appDep']
        methods_path = config['appMet']
        obj_path = config['appPath']
    return config


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
