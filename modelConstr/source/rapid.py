import imp
import json
import optparse
import os
import sys

import Classes
import representset
import xmlgen
from Parsing_Util.readFact import readFact
from optimality import findOptimal
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
calRS = False
qosRun = False
validate = False
validate_rs_path = ""

NUM_OF_FIXED_ENV = -1

THRESHOLD = 0.05
RS_THRESHOLD = 0.05


def main(argv):
    global groundTruth_profile, knob_samples, knobs, mode, methods_path, desc, \
        calRS, validate, validate_rs_path
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
            None, lvl)
        finalized_xml = completeXML(appname, xml, cost_rsdg, mv_rsdgs[0],
                                    model, True)
        # append the xml path to the file
        config['finalized_rsdg'] = os.path.abspath(finalized_xml)
        config_file = open(run_config_path, 'w')
        json.dump(config, config_file, indent=2, sort_keys=True)
        config_file.close()
        return

    if (mode == "optimality"):
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
        max_cost = appMethod.max_cost
        min_cost = appMethod.min_cost
        step_size = (max_cost - min_cost) / 20.0
        default_optimals = []
        # first get all the pareto-optimal points in default settings
        for pref in preferences:
            pref = 1.0
        factfile, mvfactfile = genFactWithRSDG(appname, groundTruth_profile,
                                               cost_rsdg, mv_rsdgs, appMethod,
                                               preferences)
        readFact(factfile, knobs, groundTruth_profile)
        readFact(mvfactfile, knobs, groundTruth_profile, False)
        for percentage in range(1, 20):
            budget = (min_cost + float(percentage) * step_size)
            default_optimals.append(findOptimal(groundTruth_profile, budget)[0])
        # now iterate through all possible preferences
        mv_under_budget = {}
        id = 0
        for submetric in preferences:
            for pref in range(1, 10, 1):
                # setup new preferences
                new_pref = []
                for i in range(0, len(preferences)):
                    if i == id:
                        new_pref.append(1.0 + float(pref))
                    else:
                        new_pref.append(1.0)
                factfile, mvfactfile = genFactWithRSDG(appname,
                                                       groundTruth_profile,
                                                       cost_rsdg, mv_rsdgs,
                                                       appMethod,
                                                       new_pref)
                readFact(factfile, knobs, groundTruth_profile)
                readFact(mvfactfile, knobs, groundTruth_profile, False)
                # calculate the new optimal configs
                mv_loss = []
                for percentage in range(1, 20):
                    budget = (min_cost + float(percentage) * step_size)
                    real_optimal = findOptimal(groundTruth_profile, budget)[1]
                    default_optimal = \
                        groundTruth_profile.getMV(
                            default_optimals[percentage - 1])[
                            -1]
                    mv_loss.append(default_optimal / real_optimal)
                # get the preference in string
                pref_string = "-".join(map(lambda x: str(x), new_pref))
                mv_under_budget[pref_string] = mv_loss
            id += 1
        # report only the worst case
        worst_cases = []
        for cur_budget in range(0, 19):
            cur_worst = 100
            for item, values in mv_under_budget.items():
                if values[cur_budget] < cur_worst:
                    cur_worst = values[cur_budget]
            worst_cases.append(cur_worst)
        print
        worst_cases
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
        fulltraining_size = len(groundTruth_profile.configurations)
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
        factfile, mvfactfile, time_record = genFact(
            appname, groundTruth_profile, appMethods, withQoS, withSys,
            withPerf, NUM_OF_FIXED_ENV)
        # ######################STAGE-3########################
        # third stage: Modeling, use the specific modeling method to construct
        # the RSDG
        readFact(factfile, knobs, groundTruth_profile)
        if withQoS:
            readFact(mvfactfile, knobs, groundTruth_profile, False)
        groundTruth_profile.printProfile("./outputs/" + appname + ".profile")
        # if it's just model validation
        if validate:
            rs_configs = representset.getConfigurationsFromFile(
                validate_rs_path, knobs)
            representset.validateRS(groundTruth_profile, rs_configs)
            return
        # construct the cost rsdg iteratively given a threshold
        cost_rsdg, mv_rsdgs, cost_path, mv_paths, seglvl, training_time, \
        rsp_size = \
            constructRSDG(
                groundTruth_profile, knob_samples, THRESHOLD, knobs, True,
                model,
                time_record)

        # Generate the representative set
        rss_size = 0
        if calRS:
            rs, mean = representset.genContRS(groundTruth_profile, RS_THRESHOLD)
            rss_size = len(rs)
            with open(appname + ".rs", 'w') as result:
                for config in rs:
                    result.write(config.printSelf(",") + "\n")
                result.write(str(mean))
            # calculate training time for RS
            if time_record is not None:
                total_time = 0.0
                for config in rs:
                    total_time += time_record[config.printSelf("-")]
                training_time['RS'] = total_time

        # write training time to file
        if time_record is not None:
            with open('time_compare.txt', 'w') as file:
                file.write(json.dumps(training_time, indent=2, sort_keys=True))
        if PLOT:
            draw("outputs/modelValid.csv")

        with open('./training_size.txt', 'w') as ts:
            ts.write("full:" + str(fulltraining_size) + "\n")
            ts.write("rsp:" + str(rsp_size) + "\n")
            ts.write("rss:" + str(rss_size) + "\n")

        # ######################STAGE-4########################
        # forth stage, generate the final RSDG in XML format
        default_xml_path = completeXML(appname, xml, cost_rsdg, mv_rsdgs[-1],
                                       model)

        # cleaning
        os.system("rm *.log")

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

        if qosRun:
            mvs = appMethods.qosRun()
            with open("./qos_report_" + appname + "_" + model + ".txt",
                      'w') as report:
                for mv in mvs:
                    report.write(str(mv))
                    report.write("\n")

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
    global app_config, observed, fact, KF, remote, model, rs, stage, mode, \
        PLOT, config_file, run_config_path
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
    global desc, methods_path, obj_path, withSys, withQoS, withPerf, calRS, \
        qosRun, validate, validate_rs_path
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
        if 'RS' in config:
            calRS = config['RS'] == 1
        if 'qosRun' in config:
            qosRun = config['qosRun'] == 1
        if 'validate_rs_path' in config:
            validate = config['validate_rs_path'] != ""
            validate_rs_path = config['validate_rs_path']
    return config


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
