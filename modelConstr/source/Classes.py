# Neccesary Data-Structures used in RAPID-C

class Knobs:
    def __init__(self):
        self.knobs = {}
    def addKnob(self,knob):
        self.knobs[knob.set_name] = knob
    def getKnob(self,name):
        return self.knobs[name]

# a knob setting with max and min settings, smallest unit for RAPID-C
class Knob:
    def __init__(self,svc_name,set_name,min,max):
        self.svc_name = svc_name
        self.set_name = set_name
        self.min = int(min)
        self.max = int(max)

# a config for a certain knob
class Config:
    def __init__(self,knob,val):
        self.knob = knob
        self.val = val

# configuration consists of multiple config's, each of which represents a knob configuration
class Configuration:
    def __init__(self):
        self.knob_settings = []
    def addConfig(self,config):
        for c in config:
            self.knob_settings.append(c)
    def retrieve_configs(self):
        return self.knob_settings

###################problem generation#########################

# a continuous constraint with source and sink
class Constraint:
    def __init__(self,type,source,sink,source_min,source_max,sink_min,sink_max):
        self.type = type
        self.source = source
        self.sink = sink
        self.source_min = int(source_min)
        self.source_max = int(source_max)
        self.sink_min = int(sink_min)
        self.sink_max = int(sink_max)

class Segment:
    def __init__(self,seg_name,knob_name,min,max):
        self.seg_name =seg_name
        self.knob_name = knob_name
        self.min = min
        self.max = max
    def setID(self,id):
        self.id = id
    def printID(self):
        return self.seg_name+"_"+str(self.id)
    def printVar(self):
        return self.seg_name+"_"+str(self.id)+"_V"
    def setCoeff(self,a,b):
        self.a = a
        self.b = b

###################parsing classes#############################

# a profile table, could be observed, or ground truth
class Profile:
    def __init__(self):
        self.profile_table = {}
        self.configurations = set()
    def addEntry(self,config,cost):
        self.profile_table[self.hashConfig(config)]=cost
        self.configurations.add(config)
        return
    def hashConfig(self,configuration):
        tmp_map = {}
        settings = configuration.retrieve_configs()
        for c in settings:
            name = c.knob.set_name
            val = c.val
            tmp_map[name] = val
        hash_result = ""
        sorted(settings)
        for m in tmp_map:
            hash_result+=m+","+str(tmp_map[m])+","
        hash_result = hash_result[:-1]
        return hash_result
    def setCost(self,configuration,cost):
        self.profile_table[self.hashConfig(configuration)] = cost
    def getCost(self,configuration):
        entry = self.hashConfig(configuration)
        return self.profile_table[entry]
    def hasEntry(self,configuration):
        return self.hashConfig(configuration) in self.profile_table
    def printProfile(self,outputfile):
        output = open(outputfile,'w')
        for i in sorted(self.profile_table):
            output.write(i)
            output.write(",")
            output.write(str(self.profile_table[i]))
            output.write("\n")
        output.close()
