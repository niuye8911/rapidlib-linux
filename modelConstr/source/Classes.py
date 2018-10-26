# Neccesary Data-Structures used in RAPID-C
import time
import datetime
import os


class Knob:
    """a knob setting with max and min settings. It's the smallest unit for RAPID-C
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

    def printSelf(self):
        """ print the configuration to a readable string, separated by white-space
        :return: as described
        """
        result = ""
        for config in self.knob_settings:
            result += " " + config.knob.set_name + " " + str(config.val)
        return result


###################problem generation#########################

class Constraint:
    """ a continuous constraint with source and sink
    The syntax of a constraint is:
    if sink_min <= sink <= sink_max, then source_min <= source <= source_max
    """

    def __init__(self, type, source, sink, source_min, source_max, sink_min, sink_max):
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


###################parsing classes#############################

class Profile:
    """ a profile table, could be observed, or ground truth
    """

    def __init__(self):
        """ Initialization
        """
        self.profile_table = {}
        self.configurations = set()
        self.mvprofile_table = {}

    def addCostEntry(self, configuration, cost):
        """ Record the cost for a configuration
        :param configuration: the configuration
        :param cost: the cost
        """
        self.profile_table[self.hashConfig(configuration)] = cost
        self.configurations.add(configuration)
        return

    def addMVEntry(self, configuration, mv):
        """ Record the MV for a configuration
        :param configuration: the configuration
        :param mv: the mv
        """
        self.mvprofile_table[self.hashConfig(configuration)] = mv
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
            print "cannot found entry"
            hashcode = self.hashConfig(configuration)
            print configuration.printSelf(), hashcode
            print self.profile_table
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

    def setMV(self, configuration, val):
        """Set the MV of a configuration
        :param configuration: the configuration
        :param val: the MV
        """
        self.mvprofile_table[self.hashConfig(configuration)] = val

    def getMV(self, configuration):
        """Get the MV of a configuration
        :param configuration: the configuration
        :return: the MV
        """
        entry = self.hashConfig(configuration)
        return self.mvprofile_table[entry]

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
            output.write(str(self.profile_table[i]) + ",")
            output.write(str(self.mvprofile_table[i]))
            output.write("\n")
        output.close()


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
        if not a in self.coeffTable:
            self.coeffTable[a] = {}
        if not b in self.coeffTable[a]:
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
                rsdg.write(knob + "_" + b + ":" + str(self.coeffTable[knob][b].a) + "/" + str(
                    self.coeffTable[knob][b].b) + "/" + str(self.coeffTable[knob][b].c) + "\n")
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
            totalcost += coeffs[0] * knob_val * knob_val + coeffs[1] * knob_val + coeffs[2]

        # calculate inter cost
        configs = []
        for config in configuration.retrieve_configs():
            configs.append(config)
        for i in range(0, len(configs)):
            for j in range(0, len(configs)):
                if i == j:
                    continue
                if configs[i].knob.set_name in self.coeffTable:
                    if configs[j].knob.set_name in self.coeffTable[configs[i].knob.set_name]:
                        knoba_val = configs[i].val
                        knobb_val = configs[j].val
                        coeff_entry = self.coeffTable[configs[i].knob.set_name]
                        coeff_inter = coeff_entry[configs[j].knob.set_name]
                        a, b, c = coeff_inter.retrieveCoeffs()
                        totalcost += float(knoba_val) * float(knoba_val) * a + float(knobb_val) * float(
                            knobb_val) * b + float(knobb_val) * float(knoba_val) * c

        return totalcost


class pieceRSDG:
    """A RSDG calculated based on piece-wise linear regression model
    """

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
        if not a in self.coeffTable:
            self.coeffTable[a] = {}
        if not b in self.coeffTable[a]:
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
        # print the segments
        for knob in self.knob_table:
            seglist = self.knob_table[knob]
            rsdg.write(knob + "\n")
            for seg in seglist:
                rsdg.write("\t")
                rsdg.write(str(seg.min) + " " + str(seg.max) + " ")
                rsdg.write(seg.printID() + " " + str(seg.a) + " " + str(seg.b) + "\n")
            rsdg.write("\n")
        # print the coeff
        rsdg.write("COEFF\n")
        for knob in self.coeffTable:
            for b in self.coeffTable[knob]:
                rsdg.write("\t")
                rsdg.write(knob + "_" + b + ":" + str(self.coeffTable[knob][b].a) + "/" + str(
                    self.coeffTable[knob][b].b) + "/" + str(self.coeffTable[knob][b].c) + "\n")
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
                    if configs[j].knob.set_name in self.coeffTable[configs[i].knob.set_name]:
                        knoba_val = configs[i].val
                        knobb_val = configs[j].val
                        coeff_entry = self.coeffTable[configs[i].knob.set_name]
                        coeff_inter = coeff_entry[configs[j].knob.set_name]
                        a, b, c = coeff_inter.retrieveCoeffs()
                        totalcost += float(knoba_val) * float(knoba_val) * a + float(knobb_val) * float(
                            knobb_val) * b + float(knobb_val) * float(knoba_val) * c
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
    Developers will inherit from this class to implement the app-specific methods. RAPID(C) will run their
    implementations to
    1) get the groundtruth of the app by running the app in default mode.
    2) get the training data by running the app in different configurations
    """

    def __init__(self, name):
        """ Initialization with app name
        :param name:
        """
        self.appName = name

    # Implement this function
    def train(self, config_table, costFact, mvFact, withMV, withSys):
	""" Train the application with all configurations in config_table and write Cost / Qos in costFact and mvFact.
	:param config_table: A table of class Profile containing all configurations to train
	:param costFact: the destination of output file for recording costs
	:param mvFact: the destination of output file for recording MV
    :param withMV: whether to check MV or not
    :param withSys: whether to check system usage or not
	"""
        # perform a single run for training
        pass

    # Implement this function
    def runGT(self):
        """ Perform a default run of non-approxiamte version of the application to generate groundtruth result for QoS checking later in the future. The output can be application specific, but we recommend to output the result to a file.
	"""
        pass

    # Some default APIs

    def getName(self):
        """ Return the name of the app
        :return: string
        """
        return self.name

    def setPath(self, mv, cost):
        """ Set the path to mv and cost fact files
        :param mv: path to mv.fact
        :param cost: path to cost.fact
        """
        self.mv_path = mv
        self.cost_path = cost

    def getCostPath(self):
        """ Get the path to cost.fact
        :return: string
        """
        return self.cost_path

    def getMVPath(self):
        """ Get the path to mv.fact
        :return: string
        """
        return self.mv_path

    ### some utilities might be useful

    def getTime(self, command, work_units=1, withSys=False):
        """ return the execution time of running a single work unit using func in milliseconds
        To measure the cost of running the application with a configuration, each training run may finish multiple
        work units to average out the noise.
        :param command: The shell command to use in format of ["app_binary","arg1","arg2",...]
        :param work_units: The total work units in each run
        :param withSys: whether to check system usage or not
        :return: the average execution time for each work unit
        """
        time1 = time.time()
        if withSys:
            # reassemble the command with pcm calls
            # sudo ./pcm.x -csv=results.csv
            pcm_prefix = ['/home/liuliu/Research/pcm/pcm.x', '-csv=tmp.csv', '--']
            command = pcm_prefix + command
            print command
        os.system(" ".join(command))
        time2 = time.time()
        avg_time = (time2 - time1) * 1000.0 / work_units
        # parse the csv
        with open('tmp.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            line_count = 0
            metric = []
            value = []
            metric_value = {}
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                elif line_count == 1:  # header line
                    for item in row:
                        metric.append(item)
                    line_count += 1
                else:  # value line
                    for item in row:
                        value.append(item)
            for i in range(0, len(metric)):
                metric_value[metric[i]] = value[i]
        return avg_time, metric_value

    def getSysUsage(self, ):
        """ return the average system usage for a period of time
        :return: the system usage
        """
        time1 = time.time()
        os.system(" ".join(command))
        time2 = time.time()
        return (time2 - time1) * 1000.0 / work_units

    def moveFile(self, fromfile, tofile):
        """ move a file to another location
        :param fromfile: file current path
        :param tofile: file new path
        """
        command = ["mv", fromfile, tofile]
        os.system(" ".join(command))

    def writeConfigMeasurementToFile(self, filestream, configuration, value):
        """ write a configuration with its value (could be cost or mv) to a opened file stream
        :param filestream: the file stream, need to be opened with 'w'
        :param configuration: the configuration
        :param value: the value in double or string
        """
        filestream.write(configuration.printSelf() + " ")
        filestream.write(str(value) + "\n")

    def pinTime(self, filestream):
        filestream.write(str(datetime.datetime.now())+" ")
