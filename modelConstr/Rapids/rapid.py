import imp
import json
import optparse
import os
import sys

import representset
import xmlgen
import csv
from Rapids_Classes.Profile import Profile
from Rapids_Classes.AppMethods import AppMethods
from Rapids_Classes.KDG import *
from App.AppSummary import AppSummary
from Parsing_Util.readFact import readFact
from optimality import findOptimal
from plot import draw
from stage_1.training import genTrainingSet
from stage_2.trainApp import genFact, genFactWithRSDG
from stage_4.constructRSDG import constructRSDG, populate
from Machine_Trainer.MachineTrainer import MachineTrainer
from xmlgen import completeXML
from util import genOfflineFact, updateAppMinMax
from collections import OrderedDict

# CMD line Parmeters
stage = -1
model = "piecewise"
mode = "standard"
config_file = ""

# Deprecated CMD arguments
observed = ""
fact = ""
KF = ""
app = ""
rs = "set"
remote = False

# Training Objs
appInfo = None  # an object of class AppSummary
groundTruth_profile = Profile()
knobs = Knobs()
knob_samples = {}

# Training Options
GRANULARITY = 10.0
PLOT = False
NUM_OF_FIXED_ENV = 30  # -1:random environment N:N fixed environments
targetMax = 0.1
targetMean = 0.05
THRESHOLD = 0.05
RS_THRESHOLD = 0.05

RSRUN = False
OVERHEAD_RUN_BUDGETS = [0.2, 0.5, 0.8, 1.1]


def main(argv):
    global appInfo, config_file, groundTruth_profile, knob_samples, knobs, mode, model

    # parse the argument
    parser = declareParser()
    options, args = parser.parse_args()
    # insert to global variables
    parseCMD(options)

    prepare()

    if (mode == "machine"):
        machineTrainer = MachineTrainer()
        machineTrainer.train()
        return

    if (mode == "finalize"):  # TODO:need to update appINFO related
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

        knobs, groundTruth_profile, knob_samples = genTrainingSet(appInfo.DESC, GRANULARITY)
        xml = xmlgen.genxml(appInfo.APP_NAME, "", "", True, appInfo.DESC, True)
        factfile, mvfactfile = genFactWithRSDG(appname, groundTruth_profile,
                                               cost_rsdg, mv_rsdgs, appMethod,
                                               preferences)
        readFact(factfile, knobs, groundTruth_profile)
        readFact(mvfactfile, knobs, groundTruth_profile, False)
        groundTruth_profile.printProfile("./outputs/" + appname + 'gen' +
                                         ".profile")
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
            desc, GRANULARITY)
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
            default_optimals.append(
                findOptimal(groundTruth_profile, budget)[0])
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
                                                       appMethod, new_pref)
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
                pref_string = "-".join(list(map(lambda x: str(x), new_pref)))
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
        return

    if mode == "standard":
        # initialize the app summary info
        appInfo = AppSummary(config_file)
        appInfo.printSummary()
        appname = appInfo.APP_NAME
        # ######################STAGE-1########################
        # generate initial training set

        knobs, groundTruth_profile, knob_samples, bb_profile = genTrainingSet(
            appInfo.DESC, GRANULARITY)
        fulltraining_size = len(groundTruth_profile.configurations)
        bb_size = len(bb_profile.configurations)
        # generate the structural RSDG files (XML)
        xml = xmlgen.genxml(appInfo.APP_NAME, "", "", True, appInfo.DESC)
        if (stage == 1):
            return

        # ######################STAGE-2########################
        # train the application

        # load user-supplied methods
        time_record = genFact(appInfo, groundTruth_profile, bb_profile,
                              NUM_OF_FIXED_ENV)
        # ######################STAGE-3########################
        # third stage: Modeling, use the specific modeling method to construct
        # the RSDG
        readFact(appInfo.FILE_PATHS['COST_FILE_PATH'], knobs,
                 groundTruth_profile)
        readFact(appInfo.FILE_PATHS['COST_FILE_PATH'], knobs, bb_profile)
        if appInfo.TRAINING_CFG['withQoS']:
            readFact(appInfo.FILE_PATHS['MV_FILE_PATH'], knobs,
                     groundTruth_profile, False)
            readFact(appInfo.FILE_PATHS['MV_FILE_PATH'], knobs, bb_profile,
                     False)
        groundTruth_profile.printProfile(appInfo.FILE_PATHS['PROFILE_PATH'])
        # if it's just model validation
        if appInfo.TRAINING_CFG['validate']:
            rs_configs = representset.getConfigurationsFromFile(
                appInfo.VALIDATE_RS_PATH, knobs)
            representset.validateRS(groundTruth_profile, rs_configs)
            return
        # construct the cost rsdg iteratively given a threshold
        if not model == "offline":
            cost_rsdg, mv_rsdgs, cost_path, mv_paths, seglvl, training_time, rsp_size = constructRSDG(
                groundTruth_profile, knob_samples, THRESHOLD, knobs, True,
                model, time_record)
        #cost_bb_rsdg, mv_bb_rsdgs, cost_bb_path, mv_bb_paths, seglvl_bb, training_time_full, rsp_bb_size = constructRSDG(
        #    bb_profile,
        #    knob_samples,
        #    THRESHOLD,
        #    knobs,
        #    True,
        #    model,
        #    time_record,
        #    KDG=False)
        #training_time.update(training_time_full)

        # Generate the representative set
        rss_size = 0
        rss_bb_size = 0
        rs = []
        rs_bb = []
        if appInfo.TRAINING_CFG['calRS'] or RSRUN:
            rs, mean = representset.genContRS(groundTruth_profile,
                                              RS_THRESHOLD)
            #rs_bb, mean_bb = representset.genContRS(bb_profile,
            #                                        RS_THRESHOLD,
            #                                        KDG=False)
            # generate the rsdg recorvered by rs
            subprofile, partitions = groundTruth_profile.genRSSubset(rs)
            costrsdg_rs, mvrsdgs_rs, costpath_rs, mvpaths_rs = populate(
                subprofile, partitions, model, KDG=False, RS=True)
            rss_size = len(rs)
            rss_bb_size = len(rs_bb)
            with open("./outputs/" + appname + '/'+appname + ".rs", 'w') as result:
                for config in rs:
                    result.write(config.printSelf(",") + "\n")
                result.write(str(mean))
            with open("./outputs/" + appname + '/'+appname + "_bb.rs", 'w') as result:
                for config in rs_bb:
                    result.write(config.printSelf(",") + "\n")
                result.write(str(mean))
            # calculate training time for RS
            if time_record is not None:
                total_time = 0.0
                total_time_bb = 0.0
                for config in rs:
                    if config.printSelf("-") in time_record:
                        total_time += time_record[config.printSelf("-")]
                for config in rs_bb:
                    if config.printSelf("-") in time_record:
                        total_time_bb += time_record[config.printSelf("-")]
                training_time['RS'] = total_time
                training_time['RS_bb'] = total_time_bb
        # write training time to file
        if time_record is not None and not model == "offline":
            with open('./outputs/' + appname + '/' + 'time_compare.txt',
                      'w') as file:
                file.write(json.dumps(training_time, indent=2, sort_keys=True))
        if PLOT:
            draw("outputs/modelValid.csv")
        if not model == "offline":
            with open("./outputs/" + appname + '/training_size.txt', 'w') as ts:
                ts.write("full:" + str(bb_size) + "\n")
                ts.write("kdg:" + str(fulltraining_size) + "\n")
                ts.write("rsp:" + str(rsp_size) + "\n")
                ts.write("rss:" + str(rss_size) + "\n")
            #ts.write("rsp_bb:" + str(rsp_bb_size) + "\n")
            #ts.write("rss_bb:" + str(rss_bb_size) + "\n")

        # ######################STAGE-4########################
        # forth stage, generate the final RSDG in XML format
        if not model == "offline":
            if not RSRUN:
                default_xml_path = completeXML(appInfo.APP_NAME, xml,
                                               cost_rsdg, mv_rsdgs[-1], model)
            else:
                default_xml_path = completeXML(appInfo.APP_NAME, xml,
                                               costrsdg_rs, mvrsdgs_rs[-1],
                                               model)
                cost_path = costpath_rs
                mv_paths = mvpaths_rs

        # cleaning
        try:
            os.system("rm *.log")
        except:
            pass

        # write the generated RSDG back to desc file
        if True:
            with open(appInfo.OUTPUT_DIR_PREFIX + appInfo.APP_NAME + "_run.config", 'w') as runFile:
                run_config = OrderedDict()
                # for missions
                run_config['basic']={}
                basic_config = run_config['basic']
                basic_config['app_name'] = appInfo.APP_NAME
                basic_config['cost_path'] = os.path.abspath(appInfo.FILE_PATHS['COST_FILE_PATH'])
                basic_config['mv_path'] = os.path.abspath(appInfo.FILE_PATHS['MV_FILE_PATH'])
                basic_config['defaultXML'] = "outputs/"+appInfo.APP_NAME+'-default.xml' if model=="offline" else os.path.abspath(default_xml_path)
                    # some extra
                run_config['mission']={}
                mission_config = run_config['mission']
                mission_config['budget'] = 0.0
                mission_config['UNIT_PER_CHECK'] = 0
                mission_config['OFFLINE_SEARCH'] = False
                mission_config['REMOTE'] = False
                mission_config['GUROBI'] = True
                mission_config['CONT'] = True
                mission_config['RAPID_M'] = False
                mission_config['RUSH_TO_END'] = False
                mission_config['MISSION_LOG'] = True
                mission_config['budget'] = 0.0

                # for custom qos
                run_config['cost_rsdg'] = "" if model=="offline" else  os.path.abspath(cost_path)
                run_config['mv_rsdgs'] = [] if model=="offline" else  list(
                    map(lambda x: os.path.abspath(x), mv_paths[0:-1]))
                run_config['mv_default_rsdg'] = [] if model=="offline" else os.path.abspath(mv_paths[-1])
                run_config['appMet'] = os.path.abspath(appInfo.METHODS_PATH)
                run_config['rapidScript'] = os.path.abspath('./rapid.py')
                run_config['seglvl'] = 0 if model=="offline" else  seglvl
                run_config['desc'] = os.path.abspath(appInfo.DESC)
                run_config['preferences'] = [] if model=="offline" else list(
                    map(lambda x: 1.0, mv_paths[0:-1]))
                json.dump(run_config, runFile, indent=2)
                runFile.close()


        if (stage == 4):
            return

        module = imp.load_source("", appInfo.METHODS_PATH)
        appMethods = module.appMethods(appInfo.APP_NAME, appInfo.OBJ_PATH)
        # update the min/max value
        updateAppMinMax(appInfo, appMethods)
        # set the run config
        appMethods.setRunConfigFile(appInfo.OUTPUT_DIR_PREFIX + appInfo.APP_NAME + "_run.config")

        if appInfo.TRAINING_CFG['qosRun']:
            if model == 'offline':
                genOfflineFact(appInfo.APP_NAME)
            report = appMethods.qosRun(OFFLINE=model == "offline")
            output_name = './outputs/' + appname + "/qos_report_" + appInfo.APP_NAME + "_" + model + ".csv"
            columns = [
                'Percentage', 'MV', 'Augmented_MV', 'Budget', 'Exec_Time'
            ]
            with open(output_name, 'w') as output:
                writer = csv.DictWriter(output, fieldnames=columns)
                writer.writeheader()
                for data in report:
                    writer.writerow(data)

        if appInfo.TRAINING_CFG['overheadRun'] and model == 'piecewise':
            for budget in OVERHEAD_RUN_BUDGETS:
                report = appMethods.overheadMeasure(budget)
                #output_name = './outputs/' + appname + "/overhead_report_" + appInfo.APP_NAME + "_" + str(budget) + ".csv"
                output_name = './outputs/' + appname + "/overhead_report_" + appInfo.APP_NAME + "_" + str(
                    budget) + ".csv"
                columns = [
                    'Unit', 'MV', 'Augmented_MV', 'Budget', 'Exec_Time',
                    'OverBudget', 'RC_TIME', 'RC_NUM', 'RC_by_budget',
                    'SUCCESS', 'overhead_pctg'
                ]
                with open(output_name, 'w') as output:
                    writer = csv.DictWriter(output, fieldnames=columns)
                    writer.writeheader()
                    for data in report:
                        writer.writerow(data)

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
    return 0


def declareParser():
    global mode, model
    parser = optparse.OptionParser()
    parser.add_option('-f', dest="fact")
    parser.add_option('-k', dest="KF")
    parser.add_option('--k1', dest="KF1")
    parser.add_option('--k2', dest="KF2")
    parser.add_option('-m', dest="mode", default=mode)
    parser.add_option('-o', dest="observed")
    parser.add_option('--r1', dest="r1")
    parser.add_option('--r2', dest='r2')
    parser.add_option('-r', dest='remote')
    parser.add_option('--model', dest="model", default=model)
    parser.add_option("-p", dest="plot")
    parser.add_option('--rs', dest="rs")
    parser.add_option('--rsdg', dest="rsdg")
    parser.add_option('--rsdgmv', dest="rsdgmv")
    parser.add_option('--stage', dest='stage')
    parser.add_option('-C', dest="config", default="")
    parser.add_option('--cfg', dest="run_cfg", default="")
    return parser


def parseCMD(options):
    global app_config, observed, fact, KF, remote, model, rs, stage, mode, \
        PLOT, config_file, run_config_path, RSRUN
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
        print(" ERROR: no run config provided for finalization")
        exit()
    if options.mode == "standard" and options.config == "":
        print(" ERROR: missing application config, use -C to provide")
        exit()
    if options.model == "rs":
        print("RUNNING Representative Set")
        RSRUN = True
    if options.config is not None:
        config_file = options.config
    if options.stage is not None:
        stage = int(options.stage)


def prepare():
    # prepare the output dirs
    if not os.path.exists("./outputs"):
        os.system("mkdir outputs")
    if not os.path.exists("./debug"):
        os.system("mkdir debug")
    if not os.path.exists("./training_outputs"):
        os.system("mkdir training_outputs")


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
