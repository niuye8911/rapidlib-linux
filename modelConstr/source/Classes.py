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
    def getSetting(self, knob_name):
        for c in self.knob_settings:
            if knob_name == c.knob.set_name:
                return c.val
    def printSelf(self):
        result = ""
        for config in self.knob_settings:
            result+="/"+config.knob.set_name + "/" + str(config.val)
        return result

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
        self.a = 0.0
        self.b = 0.0
    def setID(self,id):
        self.id = id
    def printID(self):
        return self.seg_name+"_"+str(self.id)
    def printVar(self):
        return self.seg_name+"_"+str(self.id)+"_V"
    def printConst(self):
        return self.seg_name + "_" + str(self.id) + "_C"
    def setLinearCoeff(self,a):
        self.a = a
    def setConstCoeff(self, b):
        self.b = b

###################parsing classes#############################

# a profile table, could be observed, or ground truth
class Profile:
    def __init__(self):
        self.profile_table = {}
        self.configurations = set()
        self.mvprofile_table = {}
    def addCostEntry(self, config, cost):
        self.profile_table[self.hashConfig(config)]=cost
        self.configurations.add(config)
        return
    def addMVEntry(self, config, cost):
        self.mvprofile_table[self.hashConfig(config)]=cost
        return
    def updateEntry(self,config,val,COST=True):
        table = None
        if COST:
            table = self.profile_table
        else:
            table = self.mvprofile_table
        if not self.hashConfig(config) in table:
            print "cannot found entry"
            hashcode = self.hashConfig(config)
            print config.printSelf(),hashcode
            print self.profile_table
            return
        table[self.hashConfig(config)] = val
    def hashConfig(self,configuration):
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
            hash_result+=m+","+str(tmp_map[m])+","
        hash_result = hash_result[:-1]
        return hash_result
    def setCost(self,configuration,val):
        self.profile_table[self.hashConfig(configuration)] = val
    def getCost(self,configuration):
        entry = self.hashConfig(configuration)
        return self.profile_table[entry]
    def setMV(self,configuration,val):
        self.mvprofile_table[self.hashConfig(configuration)] = val
    def getMV(self,configuration):
        entry = self.hashConfig(configuration)
        return self.mvprofile_table[entry]
    def hasEntry(self,configuration):
        hashedID = self.hashConfig(configuration)
        return hashedID in self.profile_table
    def printProfile(self,outputfile):
        output = open(outputfile,'w')
        for i in sorted(self.profile_table):
            output.write(i)
            output.write(",")
            output.write(str(self.profile_table[i])+",")
            output.write(str(self.mvprofile_table[i]))
            output.write("\n")
        output.close()


class InterCoeff:
    def __init__(self):
        self.a = 0.0
        self.b = 0.0
        self.c = 0.0
    def adda(self,a):
        self.a = a
    def addb(self, b):
        self.b = b
    def addc(self,c):
        self.c = c
    def retrieveABC(self):
        return self.a,self.b,self.c

class pieceRSDG:
    def __init__(self):
        self.knob_table = {}
        self.coeffTable = {}
    def addKnob(self,knob):
        self.knob_table[knob] = []
    def addSeg(self,knob,seg):
        self.knob_table[knob].append(seg)
    def addInterCoeff(self,a,b,val,abc):
        if not a in self.coeffTable:
            self.coeffTable[a] = {}
            self.coeffTable[a][b] = InterCoeff()
        if abc=="a":
            self.coeffTable[a][b].adda(val)
        elif abc == "b":
            self.coeffTable[a][b].addb(val)
        elif abc=="c":
            self.coeffTable[a][b].addc(val)
    def printRSDG(self,COST=True):
        outfilename = ""
        if COST:
            outfilename = "./outputs/cost.rsdg"
        else:
            outfilename = "./outputs/mv.rsdg"
        rsdg = open(outfilename,'w')
        # print the segments
        for knob in self.knob_table:
            seglist = self.knob_table[knob]
            rsdg.write(knob+"\n")
            for seg in seglist:
                rsdg.write("\t")
                rsdg.write(str(seg.min )+ " " + str(seg.max) + " ")
                rsdg.write(seg.printID() + " "+str(seg.a) + " "+str(seg.b)+"\n")
            rsdg.write("\n")
        # print the coeff
        rsdg.write("COEFF\n")
        for knob in self.coeffTable:
            for b in self.coeffTable[knob]:
                rsdg.write("\t")
                rsdg.write(knob + "_" + b + ":"+str(self.coeffTable[knob][b].a) +"/"+str(self.coeffTable[knob][b].b)+"/"+str(self.coeffTable[knob][b].c)+"\n")
        rsdg.close()
    def calCost(self,configuration):
        totalcost = 0.0
        #calculate linear cost
        for config in configuration.retrieve_configs():
            knob_name = config.knob.set_name
            knob_val = config.val
            seg = self.findSeg(knob_name, knob_val)
            totalcost += knob_val * seg.a + seg.b
        #calculate inter cost
        configs = []
        for config in configuration.retrieve_configs():
            configs.append(config)
        for i in range(0,len(configs)):
            for j in range(0,len(configs)):
                if i==j:
                    continue
                if configs[i].knob.set_name in self.coeffTable:
                    if configs[j].knob.set_name in self.coeffTable[configs[i].knob.set_name]:
                        knoba_val = configs[i].val
                        knobb_val = configs[j].val
                        coeff_entry =self.coeffTable[configs[i].knob.set_name]
                        coeff_inter = coeff_entry[configs[j].knob.set_name]
                        a,b,c = coeff_inter.retrieveABC()
                        totalcost+=float(knoba_val) * float(knoba_val) * a + float(knobb_val) * float(knobb_val) * b + float(knobb_val) * float(knoba_val) * c
        return totalcost

    def findSeg(self,knob_name,knob_val):
        seglist = self.knob_table[knob_name]
        highest = -1
        highest_seg = None
        for seg in seglist:
            if seg.max>highest:
                highest = seg.max
                highest_seg = seg
            if knob_val>=seg.min and knob_val <= seg.max:
                return seg
        # IF NOTHING MATCHES, USE THE HIGHEST SEG
        return highest_seg