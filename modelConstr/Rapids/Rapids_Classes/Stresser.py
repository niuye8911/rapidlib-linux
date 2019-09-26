# generate a new real-app stresser
import imp, os, random
from App.AppSummary import AppSummary
from stage_1.training import genTrainingSet

class Stresser:
    APP_FILES = {
        'facedetect':
        '/home/liuliu/Research/rapidlib-linux/modelConstr/data/facePort',
        'ferret':
        '/home/liuliu/Research/rapidlib-linux/modelConstr/data/facePort',
        'swaptions':
        '/home/liuliu/Research/rapidlib-linux/modelConstr/data/swapPort',
        'svm': '/home/liuliu/Research/rapidlib-linux/modelConstr/data/svmPort'
    }

    def __init__(self, target_app):
        self.target_app = target_app
        self.apps = {}
        self.loadAll()

    def loadAll(self):
        for app_name, config_file in self.APP_FILES.items():
            if app_name == self.target_app:
                continue
            app = AppSummary(config_file + '/config_algae.json')
            knobs, config_table, knob_samples, flatted_blackbox_training = genTrainingSet(
                app.DESC)
            # groundTruth_profile contains all the config_table
            module = imp.load_source("", app.METHODS_PATH)
            appMethods = module.appMethods(app.APP_NAME, app.OBJ_PATH)
            self.apps[app_name] = {
                'appMethods': appMethods,
                'configs': list(config_table.configurations)
            }

    def getRandomStresser(self):
        app = random.choice(list(self.apps.keys()))
        configuration = random.choice(self.apps[app]['configs'])
        cmd = self.apps[app]['appMethods'].getCommand(
            configuration.retrieve_configs(), qosRun=False,
            fullRun=True)  #set to true to return the full run command
        return {
            'app': app,
            'configuration': configuration.printSelf('-'),
            'command': cmd
        }
