# Neccesary Data-Structures used in RAPID-C
import csv
import datetime
import hashlib
import os
import random
import signal
import subprocess
import time
import socket
import requests


class Metric:
    EXCLUDED_METRIC = {
        "Date",
        "Time",
        "Proc Energy (Joules)",
        'C0res%',
        'C10res%',
        'C1res%',
        'C2res%',
        'C3res%',
        'C6res%',
        'C7res%',
        'C8res%',
        'C9res%',
    }

    def __init__(self, addtl_exclusion={}):
        self.metrics = dict()
        self.metric_names = []
        self.addtl_exclusion = {}

    def add_metric(self, name, value):
        if name not in self.EXCLUDED_METRIC and name not in self.addtl_exclusion:
            self.metrics[name] = value
            self.metric_names.append(name)
            self.metric_names = sorted(self.metric_names)

    def printAsCSVLine(self, delimiter):
        metricsNames = map(lambda metric: str(self.metrics[metric]),
                           self.metric_names)
        return delimiter.join(metricsNames)

    def printAsHeader(self, delimiter, leading="Configuration", id=''):
        if leading == "Configuration":
            leading = leading + delimiter
        updated_metrics = map(lambda x: x + id, self.metric_names)
        return leading + delimiter.join(sorted(updated_metrics))


class SlowDown:
    def __init__(self, configuration):
        self.configuration = configuration
        self.slowdown_table = dict()
        self.metrics = dict()

    def add_slowdown(self, metric, slowdown):
        self.slowdown_table[self.get_md5(metric).hexdigest()] = slowdown
        self.metrics[self.get_md5(metric).hexdigest()] = metric

    def get_md5(self, metric):
        return hashlib.md5(metric.printAsCSVLine(',').encode())

    def get_metric(self, md5string):
        return self.metrics[md5string].printAsCSVLine(
            ',') if md5string in self.metrics else ''

    def get_slowdown(self, metric):
        md5hex = self.get_md5(metric).hexdigest()
        return self.slowdown_table[
            md5hex] if md5hex in self.slowdown_table else -1.

    def writeSlowDownTable(self, filestream):
        # write the metric
        for metricmd5, slowdown in self.slowdown_table.items():
            # write the config
            filestream.write(self.configuration.printSelf('-'))
            filestream.write(',')
            filestream.write(self.get_metric(metricmd5))
            filestream.write(',')
            filestream.write(str(slowdown))
            filestream.write('\n')


class SysUsageTable:
    def __init__(self):
        self.table = dict()
        self.metrics = []

    def add_entry(self, configuration, metric):
        self.table[configuration] = metric
        if not self.metrics:
            self.metrics = metric.metric_names

    def printAsCSV(self, filestream, delimiter):
        # write the header
        header_written = False
        # write the body
        for configuration, metric in self.table.items():
            # write the header
            if not header_written:
                filestream.write(metric.printAsHeader(delimiter))
                filestream.write('\n')
                header_written = True
            # write the configuration
            filestream.write(configuration + delimiter)
            filestream.write(metric.printAsCSVLine(delimiter))
            filestream.write("\n")
        filestream.close()


class SysArgs:
    def __init__(self):
        self.env = {}
        self.env["cpu_num"] = [1, 2, 3, 4]
        self.env["io"] = [1, 2]
        self.env["vm"] = [1, 2]
        self.env["vm_bytes"] = ["128K", "256K", "512K"]
        self.env["hdd"] = [1, 2, 3]
        self.env["hdd_bytes"] = ["128K", "256K", "512K"]

    def getRandomEnv(self):
        cpu_num = random.choice(self.env['cpu_num'])
        io = random.choice(self.env['io'])
        vm = random.choice(self.env['vm'])
        vm_bytes = random.choice(self.env['vm_bytes'])
        hdd = random.choice(self.env['hdd'])
        hdd_bytes = random.choice(self.env['hdd_bytes'])
        command = [
            '/usr/bin/stress',
            '-q',
            "--cpu",
            str(cpu_num),
            '--io',
            str(io),
            '--vm',
            str(vm),
            '--vm-bytes',
            str(vm_bytes),
            '--hdd',
            str(hdd),
            '--hdd-bytes',
            str(hdd_bytes),
        ]
        return command


class Knob:
    """a knob setting with max and min settings. It's the smallest unit for
    RAPID-C
    """

    def __init__(self, svc_name, set_name, min, max):
        """ Initialization
        :param svc_name: name of service
        :param set_name: name of setting
        :param min: lower bound
        :param max: upper bound
        """
        self.svc_name = svc_name
        self.set_name = set_name
        self.min = int(min)
        self.max = int(max)


class Knobs:
    """ a collection of Knob
    The Knob object can be retrieved by name
    """

    def __init__(self):
        self.knobs = {}

    def addKnob(self, knob):
        """ Add a knob
        :param knob: the knob to be added
        :return: none
        """
        self.knobs[knob.set_name] = knob

    def getKnob(self, name):
        """ Get a knob
        :param name: name of the knob
        :return: the object
        """
        return self.knobs[name]


class Config:
    """ a config for a certain knob
    """

    def __init__(self, knob, val):
        """ set a knob to a value
        :param knob: a knob instance
        :param val: the value for that knob
        """
        self.knob = knob
        self.val = val


#
class Configuration:
    """ a collection of Config
    """

    def __init__(self):
        self.knob_settings = []

    def addConfig(self, config):
        """ Add a list of configs
        :param config: A list of Config instances
        :return: none
        """
        for c in config:
            self.knob_settings.append(c)

    def retrieve_configs(self):
        """ Return the list of configs
        :return: as described
        """
        return self.knob_settings

    def getSetting(self, knob_name):
        """ Get the value for a particular knob
        :param knob_name: name of the interested knob
        :return: the setting value of that knob
        """
        for c in self.knob_settings:
            if knob_name == c.knob.set_name:
                return c.val

    def __eq__(self, other):
        if isinstance(other, Configuration):
            return other.printSelf() == self.printSelf()
        else:
            return False

    def __hash__(self):
        return hash(self.printSelf())

    def printSelf(self, delimiter=' '):
        """ print the configuration to a readable string, separated by
        white-space
        :return: as described
        """
        items = map((lambda x: x.knob.set_name + delimiter + str(x.val)),
                    self.knob_settings)
        items.sort()
        return delimiter.join(sorted(items))
        # for config in self.knob_settings:
        #    result += " " + config.knob.set_name + " " + str(config.val)
        # return result


# ##################problem generation#########################


class Constraint:
    """ a continuous constraint with source and sink
    The syntax of a constraint is:
    if sink_min <= sink <= sink_max, then source_min <= source <= source_max
    """

    def __init__(self, type, source, sink, source_min, source_max, sink_min,
                 sink_max):
        """ Initialization
        :param type: AND or OR, in string
        :param source: string
        :param sink: string
        :param source_min: lower bound of source
        :param source_max: upper bound of source
        :param sink_min: lower bound of sink
        :param sink_max: upper bound of sink
        """
        self.type = type
        self.source = source
        self.sink = sink
        self.source_min = int(source_min)
        self.source_max = int(source_max)
        self.sink_min = int(sink_min)
        self.sink_max = int(sink_max)


class Segment:
    """ a segment of a knob
    The segment of knob can be used both in dependencies and constraint
    """

    def __init__(self, seg_name, knob_name, min, max):
        """ Initilization
        :param seg_name: segment name
        :param knob_name: knob name
        :param min: lower bound of the segment
        :param max: upper bound of the segment
        """
        self.seg_name = seg_name
        self.knob_name = knob_name
        self.min = min
        self.max = max
        self.a = 0.0  # the linear coefficient value
        self.b = 0.0  # the constant coefficient value

    def setID(self, id):
        """Set the id of the segment
        :param id: an integer ID
        :return: None
        """
        self.id = id

    def printID(self):
        """ Return the readable segment id
        :return: seg_name + [id]
        """
        return self.seg_name + "_" + str(self.id)

    def printVar(self):
        """ Return the variable name in LP representing the linear coefficient
        :return: a string
        """
        return self.seg_name + "_" + str(self.id) + "_V"

    def printConst(self):
        """ Return the variable name in LP representing the constant coefficient
        :return:
        """
        return self.seg_name + "_" + str(self.id) + "_C"

    def setLinearCoeff(self, a):
        """ Setter of the linear coeff
        :param a: a double value
        """
        self.a = a

    def setConstCoeff(self, b):
        """ Setter of the Constant coeff
        :param b: a double value
        """
        self.b = b


# ##################parsing classes#############################


class Profile:
    """ a profile table, could be observed, or ground truth
    """

    def __init__(self):
        """ Initialization
        """
        self.profile_table = {}
        self.configurations = set()
        self.mvprofile_table = {}
        self.numOfMVs = 1

    def removeConfig(self, configuration):
        hash_id = self.hashConfig(configuration)
        del self.profile_table[hash_id]
        del self.mvprofile_table[hash_id]
        self.configurations.remove(configuration)

    def addCostEntry(self, configuration, cost):
        """ Record the cost for a configuration
        :param configuration: the configuration
        :param cost: the cost
        """
        self.profile_table[self.hashConfig(configuration)] = cost
        self.configurations.add(configuration)
        return

    def addMVEntry(self, configuration, mvs):
        """ Record the MV for a configuration
        :param configuration: the configuration
        :param mv: the mv
        """
        self.mvprofile_table[self.hashConfig(configuration)] = mvs
        self.numOfMVs = len(mvs)
        return

    def addEntry(self, configuration, cost, mvs):
        self.addCostEntry(configuration, cost)
        self.addMVEntry(configuration, mvs)
        return

    def updateEntry(self, configuration, val, COST=True):
        """ update the value of a configuration
        :param configuration: the configuration
        :param val: the new value
        :param COST: if True, update the cost entry, else the MV entry
        """
        table = None
        if COST:
            table = self.profile_table
        else:
            table = self.mvprofile_table
        if not self.hashConfig(configuration) in table:
            print
            "cannot found entry"
            hashcode = self.hashConfig(configuration)
            print
            configuration.printSelf(), hashcode
            print
            self.profile_table
            return
        table[self.hashConfig(configuration)] = val

    def hashConfig(self, configuration):
        """ generate a unique string as ID for a configuration
        :param configuration: the configuration
        :return: a string ID for that configuration
        """
        tmp_map = {}
        settings = configuration.retrieve_configs()
        for c in settings:
            name = c.knob.set_name
            val = c.val
            tmp_map[name] = val
        hash_result = ""
        # sort the map
        tmp_map_sorted = sorted(tmp_map)
        for m in tmp_map_sorted:
            hash_result += m + "," + str(tmp_map[m]) + ","
        hash_result = hash_result[:-1]
        return hash_result

    def setCost(self, configuration, val):
        """Set the cost of a configuration
        :param configuration: the configuration
        :param val: the cost
        """
        self.profile_table[self.hashConfig(configuration)] = val

    def getCost(self, configuration):
        """Get the cost of a configuration
        :param configuration: the configuration
        :return: the cost
        """
        entry = self.hashConfig(configuration)
        return self.profile_table[entry]

    def setMV(self, configuration, vals):
        """Set the MV of a configuration
        :param configuration: the configuration
        :param vals: the MVs
        """
        self.numOfMVs = len(vals)
        self.mvprofile_table[self.hashConfig(configuration)] = vals

    def getMV(self, configuration):
        """Get the MV of a configuration
        :param configuration: the configuration
        :return: the MV
        """
        entry = self.hashConfig(configuration)
        if entry in self.mvprofile_table:
            return self.mvprofile_table[entry]
        return [0.0]

    def hasEntry(self, configuration):
        """ Check if a configuration is recorded
        :param configuration: the configuration
        :return: True if exists, else if not
        """
        hashedID = self.hashConfig(configuration)
        return hashedID in self.profile_table

    def printProfile(self, outputfile):
        """ Print the profile to a file
        :param outputfile: the path to the output
        """
        output = open(outputfile, 'w')
        for i in sorted(self.profile_table):
            output.write(i)
            output.write(",")
            if i in self.profile_table:
                output.write(str(self.profile_table[i]))
            if i in self.mvprofile_table:
                output.write("," + str(self.mvprofile_table[i]))
            output.write("\n")
        output.close()

    def genMultipleMV(self):
        profiles = []
        for i in range(0, self.numOfMVs):
            profile = Profile()
            profile.profile_table = self.profile_table
            profile.configurations = self.configurations
            profile.mvprofile_table = {
                k: v[i]
                for k, v in self.mvprofile_table.items()
            }
            profile.numOfMVs = 1
            profiles.append(profile)
        return profiles

    def genRandomSubset(self, n):
        profile = Profile()
        n = min(n, len(self.configurations))  # if not 20, then use the overall
        randomConfigs = random.sample(self.configurations, n)
        for config in randomConfigs:
            profile.addCostEntry(config, self.getCost(config))
            profile.addMVEntry(config, self.getMV(config))
        partitions = Profile.getPartitions(randomConfigs)
        return profile, partitions

    @staticmethod
    def getPartitions(configurations):
        partitions = {}
        for config in configurations:
            settings = config.retrieve_configs()
            for c in settings:
                knob_min = c.knob.min
                knob_max = c.knob.max
                name = c.knob.set_name
                val = c.val
                if name not in partitions:
                    partitions[name] = [knob_min, knob_max]
                if val not in partitions[name]:
                    partitions[name].append(val)
        for knob in partitions.keys():
            partitions[knob].sort()
        return partitions


class InterCoeff:
    """ a coefficients holder
    """

    def __init__(self):
        """Initialization
        """
        self.a = 0.0
        self.b = 0.0
        self.c = 0.0

    def addQuadCoeff(self, a):
        """Set the quad coeff
        :param a: quad coeff value
        """
        self.a = a

    def addLinearCoeff(self, b):
        """Set the linear coeff
        :param b: linear coeff value
        """
        self.b = b

    def addConstCoeff(self, c):
        """Set the constant coeff
        :param c: constant coeff value
        """
        self.c = c

    def retrieveCoeffs(self):
        """ Return the values
        :return: [quad, linear, constant]
        """
        return self.a, self.b, self.c


class quadRSDG:
    """A RSDG calculated based on quadratic regression model
    """

    def __init__(self):
        self.knob_table = {}  # constains the coefficients of all knobs
        self.coeffTable = {}

    def addKnob(self, knob):
        """ Initialize a knob
        for each entry, the value is [quad, linear, constant]
        :param knob: the knob to be added
        """
        self.knob_table[knob] = [0.0, 0.0, 0.0]

    def addKnobVal(self, knob, val, lvl):
        """ udpate the value for a knob
        :param knob: the knob
        :param val: the coeff value
        :param lvl: c -> constant, 1 -> linear, 2 (default) -> quad
        """
        if lvl == "c":
            self.knob_table[knob][2] = val
        elif lvl == "1":
            self.knob_table[knob][1] = val
        else:
            self.knob_table[knob][0] = val

    def addInterCoeff(self, a, b, abc, val):
        """ Add a inter-knob coefficient
        :param a: the first knob
        :param b: the second knob
        :param abc: the level of coefficient,
        :param val: the value
        :return:
        """
        if a not in self.coeffTable:
            self.coeffTable[a] = {}
        if b not in self.coeffTable[a]:
            self.coeffTable[a][b] = InterCoeff()
        if abc == "a":
            self.coeffTable[a][b].addQuadCoeff(val)
        elif abc == "b":
            self.coeffTable[a][b].addLinearCoeff(val)
        elif abc == "c":
            self.coeffTable[a][b].addConstCoeff(val)

    def printRSDG(self, COST=True):
        """ print the RSDG to a file
        The output path is ./outputs/[cost/mv].rsdg
        :param COST: if True, print the Cost rsdg, else the MV rsdg
        """
        outfilename = ""
        if COST:
            outfilename = "./outputs/cost.rsdg"
        else:
            outfilename = "./outputs/mv.rsdg"
        rsdg = open(outfilename, 'w')
        for knob in self.knob_table:
            rsdg.write(knob + "\n")
            rsdg.write("\t")
            rsdg.write("o2:")
            rsdg.write(str(self.knob_table[knob][0]) + " ; ")
            rsdg.write("o1:")
            rsdg.write(str(self.knob_table[knob][1]) + " ; ")
            rsdg.write("c:")
            rsdg.write(str(self.knob_table[knob][2]) + " ; \n")
        rsdg.write("COEFF\n")
        for knob in self.coeffTable:
            for b in self.coeffTable[knob]:
                rsdg.write("\t")
                rsdg.write(knob + "_" + b + ":" +
                           str(self.coeffTable[knob][b].a) + "/" +
                           str(self.coeffTable[knob][b].b) + "/" +
                           str(self.coeffTable[knob][b].c) + "\n")
        rsdg.close()

    def calCost(self, configuration):
        """ calculate the estimated cost of a configuration by RSDG
        :param configuration: the configuration
        :return: the estimated cost value
        """
        totalcost = 0.0

        # calculate linear cost
        for config in configuration.retrieve_configs():
            knob_name = config.knob.set_name
            knob_val = config.val
            coeffs = self.knob_table[knob_name]
            totalcost += coeffs[0] * knob_val * knob_val + coeffs[1] * \
                         knob_val + coeffs[2]

        # calculate inter cost
        configs = []
        for config in configuration.retrieve_configs():
            configs.append(config)
        for i in range(0, len(configs)):
            for j in range(0, len(configs)):
                if i == j:
                    continue
                if configs[i].knob.set_name in self.coeffTable:
                    if configs[j].knob.set_name in self.coeffTable[
                            configs[i].knob.set_name]:
                        knoba_val = configs[i].val
                        knobb_val = configs[j].val
                        coeff_entry = self.coeffTable[configs[i].knob.set_name]
                        coeff_inter = coeff_entry[configs[j].knob.set_name]
                        a, b, c = coeff_inter.retrieveCoeffs()
                        totalcost += float(knoba_val) * float(
                            knoba_val) * a + float(knobb_val) * float(
                                knobb_val) * b + float(knobb_val) * float(
                                    knoba_val) * c

        return totalcost


class pieceRSDG:
    """A RSDG calculated based on piece-wise linear regression model
    """

    def fromFile(self, rsdgFile):
        """ Generate a RSDG object from a file
        """
        file = open(rsdgFile, 'r')
        knob_name = ""
        segs = []
        START_COEFF = False
        for line in file:
            if START_COEFF:
                # this is the coeff lines
                [knob_a, knob_b] = line.split()[0].split(':')[0].split('_')
                [a, b, c] = line.split()[0].split(':')[1].split('/')
                self.addInterCoeff(knob_a, knob_b, float(a), 'a')
                self.addInterCoeff(knob_a, knob_b, float(b), 'b')
                self.addInterCoeff(knob_a, knob_b, float(c), 'c')
                continue

            col = line.split()
            if len(col) == 0:
                # this is the break line
                # add the knob
                self.addKnob(knob_name)
                for seg in segs:
                    self.addSeg(knob_name, seg)
                segs = []
                continue

                # add the seg
            if len(col) == 1:
                # this is the knob name line
                knob_name = col[0]
                if knob_name == "COEFF":
                    START_COEFF = True

            else:
                # this is the segment line
                [min, max, seg_name, a, b] = col
                seg = Segment(seg_name, knob_name, float(min), float(max))
                seg.setLinearCoeff(float(a))
                seg.setConstCoeff(float(b))
                seg.setID(seg_name.split('_')[1])
                segs.append(seg)

    def __init__(self):
        self.knob_table = {}
        self.coeffTable = {}

    def addKnob(self, knob):
        """ Initialize a knob entry
        for each entry, the value is a list of segments
        :param knob: the knob to be added
        """
        self.knob_table[knob] = []

    def addSeg(self, knob, seg):
        """ add a segment to the knob entry
        :param knob: the knob
        :param seg: the segment to be added
        """
        self.knob_table[knob].append(seg)

    def addInterCoeff(self, a, b, val, abc):
        """ Add a inter-knob coefficient
        :param a: the first knob
        :param b: the second knob
        :param abc: the level of coefficient,
        :param val: the value
        :return:
        """
        if a not in self.coeffTable:
            self.coeffTable[a] = {}
        if b not in self.coeffTable[a]:
            self.coeffTable[a][b] = InterCoeff()
        if abc == "a":
            self.coeffTable[a][b].addQuadCoeff(val)
        elif abc == "b":
            self.coeffTable[a][b].addLinearCoeff(val)
        elif abc == "c":
            self.coeffTable[a][b].addConstCoeff(val)

    def printRSDG(self, COST=True, id=0):
        """ print the RSDG to a file
        The output path is ./outputs/[cost/mv].rsdg
        :param COST: if True, print the Cost rsdg, else the MV rsdg
        """
        outfilename = ""
        if COST:
            outfilename = "./outputs/cost.rsdg"
        else:
            outfilename = "./outputs/mv" + str(id) + ".rsdg"
        rsdg = open(outfilename, 'w')
        # print the segments
        for knob in self.knob_table:
            seglist = self.knob_table[knob]
            rsdg.write(knob + "\n")
            for seg in seglist:
                rsdg.write("\t")
                rsdg.write(str(seg.min) + " " + str(seg.max) + " ")
                rsdg.write(seg.printID() + " " + str(seg.a) + " " +
                           str(seg.b) + "\n")
            rsdg.write("\n")
        # print the coeff
        rsdg.write("COEFF\n")
        for knob in self.coeffTable:
            for b in self.coeffTable[knob]:
                rsdg.write("\t")
                rsdg.write(knob + "_" + b + ":" +
                           str(self.coeffTable[knob][b].a) + "/" +
                           str(self.coeffTable[knob][b].b) + "/" +
                           str(self.coeffTable[knob][b].c) + "\n")
        rsdg.close()
        return outfilename

    def calCost(self, configuration):
        """ calculate the estimated cost of a configuration by RSDG
        :param configuration: the configuration
        :return: the estimated cost value
        """
        totalcost = 0.0
        # calculate linear cost
        for config in configuration.retrieve_configs():
            knob_name = config.knob.set_name
            knob_val = config.val
            seg = self.findSeg(knob_name, knob_val)
            totalcost += knob_val * seg.a + seg.b
        # calculate inter cost
        configs = []
        for config in configuration.retrieve_configs():
            configs.append(config)
        for i in range(0, len(configs)):
            for j in range(0, len(configs)):
                if i == j:
                    continue
                if configs[i].knob.set_name in self.coeffTable:
                    if configs[j].knob.set_name in self.coeffTable[
                            configs[i].knob.set_name]:
                        knoba_val = configs[i].val
                        knobb_val = configs[j].val
                        coeff_entry = self.coeffTable[configs[i].knob.set_name]
                        coeff_inter = coeff_entry[configs[j].knob.set_name]
                        a, b, c = coeff_inter.retrieveCoeffs()
                        totalcost += float(knoba_val) * float(
                            knoba_val) * a + float(knobb_val) * float(
                                knobb_val) * b + float(knobb_val) * float(
                                    knoba_val) * c
        return totalcost

    def findSeg(self, knob_name, knob_val):
        """ Locate the segment that a concrete value falls into
        :param knob_name: the knob name
        :param knob_val: the knob value
        :return: the segment that this value falls into
        """
        seglist = self.knob_table[knob_name]
        highest = -1
        highest_seg = None
        for seg in seglist:
            if seg.max > highest:
                highest = seg.max
                highest_seg = seg
            if knob_val >= seg.min and knob_val <= seg.max:
                return seg
        # IF NOTHING MATCHES, USE THE HIGHEST SEG
        return highest_seg


class AppMethods():
    """ the parent class of app-specific methods
    Developers will inherit from this class to implement the app-specific
    methods. RAPID(C) will run their
    implementations to
    1) get the groundtruth of the app by running the app in default mode.
    2) get the training data by running the app in different configurations
    """

    PCM_PREFIX = [
        '/home/liuliu/Research/pcm/pcm.x', '0.5', '-nc', '-ns', '2>/dev/null',
        '-csv=tmp.csv', '--'
    ]

    def __init__(self, name, obj_path):
        """ Initialization with app name
        :param name:
        """
        self.appName = name
        self.obj_path = obj_path
        self.sys_usage_table = SysUsageTable()
        self.training_units = 1
        self.fullrun_units = 1

    def setTrainingUnits(self, unit):
        self.training_units = unit

    # Implement this function
    def getCommand(self, configs=None, qosRun=False):
        """ Assembly the CMD line for running the app
        :param configs: a concrete configuration with knob settings
                        Default setting would assemble command for GT
        """
        return ""

    def getFullRunCommand(self, budget):
        pass

    def qosRun(self):
        print("running QOS run")
        self.runGT(True)  # first generate the groundtruth
        step_size = (self.max_cost - self.min_cost) / 10.0
        mvs = []
        for percentage in range(1, 10):
            budget = (self.min_cost + float(percentage) * step_size
                      ) * self.fullrun_units / 1000.0
            cmd = self.getFullRunCommand(budget)
            os.system(" ".join(cmd))
            # check the QoS
            mv = self.getQoS()
            if type(mv) is list:
                mv = mv[-1]  # use the default qos metric
            mvs.append(mv)
            print
            "mv:" + str(mv)
        return mvs

    # Implement this function
    def train(self, config_table, numOfFixedEnv, appInfo, upload=True):
        """ Train the application with all configurations in config_table and
        write Cost / Qos in costFact and mvFact.
        :param config_table: A table of class Profile containing all
        configurations to train
        :param numOfFixedEnv: number of environments if running for fixed env
        :param appInfo: a obj of Class AppSummary
        :param upload: whether to upload the measuremnet to RAPID_M server
        """
        # perform a single run for training
        configurations = config_table.configurations  # get the
        # configurations in the table
        train_conf = appInfo.TRAINING_CFG
        withMV = train_conf['withQoS']
        withSys = train_conf['withSys']
        withPerf = train_conf['withPerf']
        withMModel = train_conf['withMModel']
        costFact = open(appInfo.FILE_PATHS['COST_FILE_PATH'], 'w')
        if withMV:
            mvFact = open(appInfo.FILE_PATHS['MV_FILE_PATH'], 'w')
        if withSys:
            sysFact = open(appInfo.FILE_PATHS['SYS_FILE_PATH'], 'w')
        if withPerf:
            slowdownProfile = open(appInfo.FILE_PATHS['PERF_FILE_PATH'], 'w')
            slowdownHeader = False
        if withMModel:
            m_slowdownProfile = open(appInfo.FILE_PATHS['M_FILE_PATH'], 'w')
            m_slowdownHeader = False

        # comment the lines below if need random coverage
        env = SysArgs()
        env_commands = []
        if numOfFixedEnv != -1:
            for i in range(0, numOfFixedEnv):  # run different environment
                env_commands.append(env.getRandomEnv())

        training_time_record = {}

        # iterate through configurations
        total = len(configurations)
        current = 1
        for configuration in configurations:
            print("*****RUNNING:" + str(current) + "/" + str(total) + "*****")
            current += 1
            # the purpose of each iteration is to fill in the two values below
            cost = 0.0
            mv = [0.0]
            configs = configuration.retrieve_configs(
            )  # extract the configurations
            # assembly the command
            command = self.getCommand(configs)

            if not appInfo.isTrained():
                # 1) COST Measuremnt
                total_time, cost, metric = self.getCostAndSys(
                    command, self.training_units, withSys,
                    configuration.printSelf('-'))
                training_time_record[configuration.printSelf('-')] = total_time
                # write the cost to file
                AppMethods.writeConfigMeasurementToFile(
                    costFact, configuration, cost)
                # 2) MV Measurement
                if withMV:
                    mv = self.getQoS()
                    # write the mv to file
                    AppMethods.writeConfigMeasurementToFile(
                        mvFact, configuration, mv)
            if not appInfo.isPerfTrained():
                # 3) SYS Profile Measurement
                if withSys:
                    self.recordSysUsage(configuration, metric)
                # 4) Performance Measurement
                if withPerf:
                    # examine the execution time slow-down
                    print("START STRESS TRAINING")
                    slowdownTable, m_slowdownTable = self.runStressTest(
                        configuration, cost, env_commands, withMModel)
                    # write the header
                    if not slowdownHeader:
                        slowdownProfile.write(metric.printAsHeader(','))
                        slowdownProfile.write(",SLOWDOWN")
                        slowdownProfile.write('\n')
                        if withMModel:
                            m_slowdownProfile.write(metric.printAsHeader(','))
                            m_slowdownProfile.write(",SLOWDOWN")
                            m_slowdownProfile.write('\n')
                        slowdownHeader = True
                    slowdownTable.writeSlowDownTable(slowdownProfile)
                    if withMModel:
                        m_slowdownTable.writeSlowDownTable(m_slowdownProfile)
                # 5) train the slowdown given a known environment
                #if withMModel:
                #print("START MModel Testing")
                #m_slowdownTable = self.runMModelTest(configuration, cost)
                #m_slowdownTable.writeSlowDownTable(m_slowdownProfile)
            self.cleanUpAfterEachRun(configs)
        # write the metric to file
        costFact.close()
        if withMV:
            mvFact.close()
        if withSys:
            self.printUsageTable(sysFact)
        if withPerf:
            slowdownProfile.close()
        if withMModel:
            m_slowdownProfile.close()
        if upload:
            print("preparing to upload to server")
            self.uploadToServer(appInfo)
        # udpate the status
        appInfo.setTrained()
        appInfo.setPerfTrained()
        return training_time_record

    # Send the system profile up to the RAPID_M server
    def uploadToServer(self, appInfo):
        # get the app system profile text
        with open(appInfo.FILE_PATHS['SYS_FILE_PATH'], 'r') as sysF:
            sys_data = sysF.read()
        # get the app performance profile text
        with open(appInfo.FILE_PATHS['PERF_FILE_PATH'], 'r') as perfF:
            perf_data = perfF.read()
        with open(appInfo.FILE_PATHS['MV_FILE_PATH'], 'r') as perfF:
            mv_data = perfF.read()
        with open(appInfo.FILE_PATHS['COST_FILE_PATH'], 'r') as perfF:
            cost_data = perfF.read()
        # get the machine id
        hostname = socket.gethostname()

        INIT_ENDPOINT = "http://algaesim.cs.rutgers.edu/rapid_server/init.php"
        INIT_ENDPOINT = INIT_ENDPOINT + "?" + 'machine=' + hostname + \
            '&app=' + appInfo.APP_NAME

        # set up the post params
        POST_PARAMS = {
            'buckets': sys_data,
            'p_model': perf_data,
            'mv': mv_data,
            'cost': cost_data
        }

        req = requests.post(url=INIT_ENDPOINT, data=POST_PARAMS)

        response = req.text
        print("response:" + response)

    # Implement this function
    def runGT(self, qosRun=False):
        """ Perform a default run of non-approxiamte version of the
        application to generate groundtruth result for
        QoS checking later in the future. The output can be application
        specific, but we recommend to output the
        result to a file.
        """
        print("GENERATING GROUND TRUTH for " + self.appName)
        command = self.getCommand(None, qosRun)
        os.system(" ".join(command))
        self.afterGTRun()

    def runStressTest(self,
                      configuration,
                      orig_cost,
                      env_commands=[],
                      withMModel=False):
        app_command = self.getCommand(configuration.retrieve_configs())
        env = SysArgs()
        slowdownTable = SlowDown(configuration)
        m_slowdownTable = SlowDown(configuration)
        # if running random coverage, create the commands
        if len(env_commands) == 0:
            for i in range(0, 10):  # run 10 different environment
                env_command = env.getRandomEnv()
                env_commands.append(env_command)
        for env_command in env_commands:
            # if withMModel, check the environment first
            if withMModel:
                command = " ".join(self.PCM_PREFIX + env_command + ['-t', '5'])
                os.system(command)
                env_metric = AppMethods.parseTmpCSV()
            # start the env
            env_creater = subprocess.Popen(
                " ".join(env_command), shell=True, preexec_fn=os.setsid)

            total_time, cost, metric = self.getCostAndSys(
                app_command, self.training_units, True,
                configuration.printSelf('-'))
            # end the env
            os.killpg(os.getpgid(env_creater.pid), signal.SIGTERM)
            # write the measurement to file
            slowdown = cost / orig_cost
            slowdownTable.add_slowdown(metric, slowdown)
            if withMModel:
                m_slowdownTable.add_slowdown(env_metric, slowdown)
        return slowdownTable, m_slowdownTable

    def runMModelTest(self, configuration, orig_cost):
        app_command = self.getCommand(configuration.retrieve_configs())
        env = SysArgs()
        slowdownTable = SlowDown(configuration)
        # if running random coverage, create the commands
        for i in range(0, 5):  # run 5 different environment
            env_command = env.getRandomEnv()
            # measure the env
            command = " ".join(self.PCM_PREFIX + env_command + ['-t', '5'])
            os.system(command)
            env_metric = AppMethods.parseTmpCSV()
            # measure the combined env
            env_creater = subprocess.Popen(
                " ".join(env_command), shell=True, preexec_fn=os.setsid)
            total_time, cost, total_metric = self.getCostAndSys(
                app_command, self.training_units, True,
                configuration.printSelf('-'))
            # end the env
            os.killpg(os.getpgid(env_creater.pid), signal.SIGTERM)
            # write the measurement to file
            slowdown = cost / orig_cost
            slowdownTable.add_slowdown(env_metric, slowdown)
        return slowdownTable

    # Some default APIs
    def getName(self):
        """ Return the name of the app
        :return: string
        """
        return self.name

    # some utilities might be useful
    def getCostAndSys(self,
                      command,
                      work_units=1,
                      withSys=False,
                      configuration=''):
        """ return the execution time of running a single work unit using
        func in milliseconds
        To measure the cost of running the application with a configuration,
        each training run may finish multiple
        work units to average out the noise.
        :param command: The shell command to use in format of ["app_binary",
        "arg1","arg2",...]
        :param work_units: The total work units in each run
        :param withSys: whether to check system usage or not
        :return: the average execution time for each work unit
        """
        time1 = time.time()
        metric_value = {}
        if withSys:
            # reassemble the command with pcm calls
            # sudo ./pcm.x -csv=results.csv

            command = self.PCM_PREFIX + command
        os.system(" ".join(command))
        time2 = time.time()
        total_time = time2 - time1
        avg_time = (time2 - time1) * 1000.0 / work_units
        # parse the csv
        if withSys:
            metric_value = AppMethods.parseTmpCSV()
            if configuration != '':
                # back up the csv_file
                os.system("mv tmp.csv ./debug/" + configuration + ".csv")

        return total_time, avg_time, metric_value

    @staticmethod
    def parseTmpCSV():
        metric_value = Metric()
        with open('tmp.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            line_count = 0
            metric = []
            values = []
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                elif line_count == 1:  # header line
                    for item in row:
                        metric.append(item)
                    line_count += 1
                else:  # value line
                    value = []
                    if len(row) != len(metric):
                        # discard the row, especially the last row
                        continue
                    for item in row:
                        value.append(item)
                    values.append(value)
            for i in range(0, len(metric)):
                if metric[i] != '':
                    try:
                        float(values[0][i])
                    except ValueError:
                        continue
                    # calculate the average value
                    avg_value = reduce((lambda x, y: (float(y[i]) + float(x))),
                                       values, 0.) / float(len(values))
                    metric_value.add_metric(metric[i], avg_value)
        csv_file.close()
        return metric_value

    def getQoS(self):
        """ Return the QoS for a configuration"""
        return [0.0]

    def moveFile(self, fromfile, tofile):
        """ move a file to another location
        :param fromfile: file current path
        :param tofile: file new path
        """
        command = ["mv", fromfile, tofile]
        os.system(" ".join(command))

    @staticmethod
    def writeConfigMeasurementToFile(filestream, configuration, values):
        """ write a configuration with its value (could be cost or mv) to a
        opened file stream
        :param filestream: the file stream, need to be opened with 'w'
        :param configuration: the configuration
        :param value: the value in double or string
        """
        filestream.write(configuration.printSelf() + " ")
        if type(values) is list:
            for value in values:
                filestream.write(str(value) + " ")
        else:
            filestream.write(str(values))
        filestream.write('\n')

    def recordSysUsage(self, configuration, metric):
        """ record the system usage of a configuration
        :param configuration: the configuration
        :param metric: the dict of metric measured
        """
        self.sys_usage_table.add_entry(configuration.printSelf('-'), metric)

    def printUsageTable(self, filestream):
        self.sys_usage_table.printAsCSV(filestream, ',')

    def cleanUpAfterEachRun(self, configs=None):
        """ This function will be called after every training iteration for a
        config
        """
        pass

    def afterGTRun(self):
        """ This function will be called after runGT()
        """
        pass

    def computeQoSWeight(self, preferences, values):
        """ This function will be called by C++ end to finalize a xml
        """
        return 0.0

    def pinTime(self, filestream):
        filestream.write(str(datetime.datetime.now()) + " ")
