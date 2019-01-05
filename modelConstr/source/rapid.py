import imp
import json
import optparse
import os
import sys

import Classes
import xmlgen
from Parsing_Util.readFact import readFact
from plot import draw
from stage_1.training import genTrainingSet
from stage_2.trainApp import genFact, genFactWithRSDG
from stage_4.constructRSDG import constructRSDG
from xmlgen import completeXML

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
groundTruth_profile = Classes.Profile()
knobs = Classes.Knobs()
knob_samples = {}
desc = ""
stage = -1
methods_path = ""
run_config_path = ""
rsdg_paths = ['./outputs/mv1.rsdg']
obj_path = ""
config_file = ""
app_config = None
PLOT = False

withSys = False
withQoS = True
withPerf = False

NUM_OF_FIXED_ENV = -1

THRESHOLD = 0.05


def main(argv):
    global groundTruth_profile, knob_samples, knobs, mode, methods_path, desc
    # parse the argument
    parser = declareParser()
    options, args = parser.parse_args()
    # insert to global variables
    parseCMD(options)

    if (mode == "finalize"):
        # parse the run_config
        with open(run_config_path) as config_json:
            config = json.load(config_json)
            methods_path = config['appMet']
            cost_rsdg = Classes.pieceRSDG()
            cost_rsdg.fromFile(config['cost_rsdg'])
            mv_rsdgs = []
            preferences = config['preferences']
            desc = config['desc']
            lvl = config['seglvl']
            for rsdg_path in config['mv_rsdgs']:
                rsdg = Classes.pieceRSDG()
                rsdg.fromFile(rsdg_path)
                mv_rsdgs.append(rsdg)
        module = imp.load_source("", methods_path)
        appMethod = module.appMethods("", obj_path)

        appname, knobs, groundTruth_profile, knob_samples = genTrainingSet(
            desc)
        appname = appname[:-1]
        xml = xmlgen.genxml(appname, "", "", True, desc, True)
        factfile, mvfactfile = genFactWithRSDG(appname, groundTruth_profile,
                                               cost_rsdg, mv_rsdgs, appMethod,
                                               preferences)
        readFact(factfile, knobs, groundTruth_profile)
        readFact(mvfactfile, knobs, groundTruth_profile, False)
        groundTruth_profile.printProfile(
            "./outputs/" + appname + 'gen' + ".profile")
        cost_rsdg, mv_rsdgs, cost_path, mv_paths, seglvl = constructRSDG(
            groundTruth_profile, knob_samples, THRESHOLD, knobs, True, model,
            lvl)
        finalized_xml = completeXML(appname, xml, cost_rsdg, mv_rsdgs[0],
                                    model, True)
        # append the xml path to the file
        config['finalized_rsdg'] = os.path.abspath(finalized_xml)
        config_file = open(run_config_path, 'w')
        json.dump(config, config_file, indent=2, sort_keys=True)
        config_file.close()
        return

    # make the output dirs
    if not os.path.exists("./outputs"):
        os.system("mkdir outputs")
    if not os.path.exists("./debug"):
        os.system("mkdir debug")
    if not os.path.exists("./training_outputs"):
        os.system("mkdir training_outputs")

    if mode == "standard":
        # ######################STAGE-1########################
        # generate initial training set
        if desc == "":
            print
            "required a description of program with option --desc"
            return
        appname, knobs, groundTruth_profile, knob_samples = genTrainingSet(
            desc)
        appname = appname[:-1]

        # generate XML files
        xml = xmlgen.genxml(appname, "", "", True, desc)
        if (stage == 1):
            return

        # ######################STAGE-2########################
        # second stage: Training, the source library will take care of the
        # training, the output is a bodytrack.fact file
        # load user-supplied methods
        module = imp.load_source("", methods_path)
        appMethods = module.appMethods(appname, obj_path)
        factfile, mvfactfile = genFact(appname, groundTruth_profile,
                                       appMethods, withQoS, withSys, withPerf,
                                       NUM_OF_FIXED_ENV)

        # ######################STAGE-3########################
        # third stage: Modeling, use the specific modeling method to construct
        # the RSDG
        readFact(factfile, knobs, groundTruth_profile)
        if withQoS:
            readFact(mvfactfile, knobs, groundTruth_profile, False)
        groundTruth_profile.printProfile("./outputs/" + appname + ".profile")
        # construct the cost rsdg iteratively given a threshold
        cost_rsdg, mv_rsdgs, cost_path, mv_paths, seglvl = constructRSDG(
            groundTruth_profile, knob_samples, THRESHOLD, knobs, True, model)
        if PLOT:
            draw("outputs/modelValid.csv")

        # ######################STAGE-4########################
        # forth stage, generate the final RSDG in XML format
        default_xml_path = completeXML(appname, xml, cost_rsdg, mv_rsdgs[-1],
                                       model)

        # cleaning
        os.system("rm *.log *.sol")

        # write the generated RSDG back to desc file
        with open('./' + appname + "_run.config", 'w') as runFile:
            run_config = {}
            run_config['cost_rsdg'] = os.path.abspath(cost_path)
            run_config['mv_rsdgs'] = map(lambda x: os.path.abspath(x),
                                         mv_paths[0:-1])
            run_config['mv_default_rsdg'] = os.path.abspath(mv_paths[-1])
            run_config['defaultXML'] = os.path.abspath(default_xml_path)
            run_config['appMet'] = os.path.abspath(methods_path)
            run_config['rapidScript'] = os.path.abspath('./rapid.py')
            run_config['seglvl'] = seglvl
            run_config['desc'] = os.path.abspath(desc)
            run_config['preferences'] = list(
                map(lambda x: 1.0, mv_paths[0:-1]))
            json.dump(run_config, runFile, indent=2, sort_keys=True)
            runFile.close()

        if (stage == 4):
            return

    # ######SOME EXTRA MODES#############

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
    parser.add_option('-m', dest="mode", default="standard")
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
    parser.add_option('--cfg', dest="run_cfg", default="")
    return parser


def parseCMD(options):
    global app_config, observed, fact, KF, remote, model, rs, stage, mode, PLOT, config_file, run_config_path
    observed = options.observed
    fact = options.fact
    model = options.model
    if options.plot == "t":
        PLOT = True
    rs = options.rs
    remote = options.remote
    mode = options.mode
    run_config_path = options.run_cfg
    # read config
    if options.mode == "finalize" and options.run_cfg == "":
        print(" WARNING: no run config provided for finalization")
        exit()
    if options.config is not None:
        config_file = options.config
        app_config = parseConfig(config_file)
    if options.stage is not None:
        stage = int(options.stage)


def parseConfig(config_file):
    global desc, methods_path, obj_path, withSys, withQoS, withPerf
    with open(config_file) as config_json:
        config = json.load(config_json)
        desc = config['appDep']
        methods_path = config['appMet']
        obj_path = config['appPath']
        if 'withSys' in config:
            withSys = config['withSys'] == 1
        if 'withQoS' in config:
            withQoS = config['withQoS'] == 1
        if 'withPerf' in config:
            withPerf = config['withPerf'] == 1
    return config


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
