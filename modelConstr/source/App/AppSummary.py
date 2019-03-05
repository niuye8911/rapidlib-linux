# A summary of an App with all output pointers and basic info
import os
import json


class AppSummary:
    def __init__(self, cfg_file):
        with open(cfg_file) as config_json:
            config = json.load(config_json)
            self.APP_NAME = config['appName']
        name = self.APP_NAME
        # create the corresponding dir if not exists
        self.OUTPUT_DIR_PREFIX = 'outputs/' + name + '/'
        self.DEBUG_DIR = 'debug/' + name + '/'
        self.TRAINING_OUTPUT_DIR = 'training_outputs/' + name + '/'
        if not os.path.exists(self.OUTPUT_DIR_PREFIX):
            os.mkdir(self.OUTPUT_DIR_PREFIX)
        # create the file paths
        self.FILE_PATHS = {}
        self.FILE_PATHS[
            'COST_FILE_PATH'] = self.OUTPUT_DIR_PREFIX + name + "-cost.fact"
        self.FILE_PATHS[
            'MV_FILE_PATH'] = self.OUTPUT_DIR_PREFIX + name + "-mv.fact"
        self.FILE_PATHS[
            'SYS_FILE_PATH'] = self.OUTPUT_DIR_PREFIX + name + "-sys.csv"
        self.FILE_PATHS[
            'PERF_FILE_PATH'] = self.OUTPUT_DIR_PREFIX + name + "-perf.csv"
        self.FILE_PATHS[
            'PERF_FILE_PATH'] = self.OUTPUT_DIR_PREFIX + name + ".profile"
        # create the training status
        self.STATUS = {}
        self.STATUS['STANDARD_TRAINED'] = os.path.exists(
            self.FILE_PATHS['COST_FILE_PATH'])
        self.STATUS['STRESS_TRAINED'] = os.path.exists(
            self.FILE_PATHS['PERF_FILE_PATH'])
        # create the training cfg for current run
        self.TRAINING_CFG = self.readFromCFG(cfg_file)

    def readFromCFG(self, config_file):
        # read additional app info from user-provided Config file
        config_dict = {
            'withSYS': False,
            'withQoS': False,
            'withPerf': False,
            'RS': False,
            'qosRun': False,
            'validate': False,
            'validate_rs_path': ''
        }
        with open(config_file) as config_json:
            config = json.load(config_json)
            self.DESC = config['appDep']
            self.METHODS_PATH = config['appMet']
            self.OBJ_PATH = config['appPath']
            if 'withSys' in config:
                config_dict['withSys'] = config['withSys'] == 1
            if 'withQoS' in config:
                config_dict['withQoS'] = config['withQoS'] == 1
            if 'withPerf' in config:
                config_dict['withPerf'] = config['withPerf'] == 1
            if 'RS' in config:
                config_dict['calRS'] = config['RS'] == 1
            if 'qosRun' in config:
                config_dict['qosRun'] = config['qosRun'] == 1
            if 'validate_rs_path' in config:
                config_dict['validate'] = config['validate_rs_path'] != ""
                self.VALIDATE_RS_PATH = config['validate_rs_path']
        return config

    def getFilePointers(self):
        # return pointers to all trained files
        return self.FILE_PATHS

    def setTrained(self):
        self.STANDARD_TRAINED = True

    def setPerfTrained(self):
        self.STRESS_TRAINED = True

    def isTrained(self):
        return self.STANDARD_TRAINED

    def isPerfTrained(self):
        return self.STRESS_TRAINED

    def printSummary(self):
        with open(self.OUTPUT_DIR_PREFIX + "summary.json", 'w') as output:
            json.dump(self.__dict__, output, indent=2)
