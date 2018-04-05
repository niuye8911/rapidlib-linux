import itertools

"stage-1 generate valid training set from constraints"
def genTrainingSet(cfg):
    configs = open(cfg, 'r')
    knobs = set()
    and_constriants = set()
    or_constraints = set()
    outfile = open('trainingset','w')
    for line in configs:
        col = line.split(' ')
        if len(col)==4:#knob definition
            knob_name = col[0]
            setting = col[1]
            setting_min = col[2]
            setting_max = col[3]
            knobs.add(knob(knob_name,setting,setting_min,setting_max))
        elif len(col)==7:#it's a edge
            type = col[0]
            sink = col[1]
            source = col[2]
            source_min = col[5]
            source_max = col[6]
            sink_min = col[3]
            sink_max = col[4]
            if type=="or":
                or_constraints.add(constraint(type,source,sink,source_min,source_max,sink_min,sink_max))
            else:
                and_constriants.add(constraint(type,source,sink,source_min,source_max,sink_min,sink_max))
    all_training = genAllTraining(knobs)
    invalid = 0
    for configs in all_training:
        finallist = []
        flat(configs,finallist)
        if validate(finallist,knobs,and_constriants,or_constraints):
            beautify(finallist,outfile)
        else:
            invalid+=1
    print("ommited in total "+str(invalid)+" settings")
    outfile.close()

def beautify(finallist,outfile):
    for i in range(len(finallist)):
        outfile.write(finallist[i].setting + "," + str(finallist[i].val))
        if not (i == len(finallist)-1):
            outfile.write(",")
    outfile.write("\n")

def flat(tup,finallist):
    if type(tup) is tuple:
        if (len(tup)==0):
            return
        flat(tup[0],finallist)
        flat(tup[1:],finallist)
    else:
        finallist.append(tup)

def genAllTraining(knobs):
    final_sets = set()
    for knob in knobs:
        single_set = []
        name = knob.set_name
        min = int(knob.min)
        max = int(knob.max)
        step = (max-min)/9.0
        if step<1:
            step = 1
        print "step size for "+name + "is " + str(step)
        i = min
        while i <= max:
            single_set.append(config(name,int(i)))
            i= i + step
        frozen_single = frozenset(single_set)
        final_sets.add(frozen_single)
    pro = {}
    inited = False;
    for i in final_sets:
       if inited:
           pro = itertools.product(pro, i)

       else:
           print "init pro"
           pro = i
           inited = True
    return pro

def validate(configs,knobs,and_constraints,or_constraints):
    config_map = dict()
    # setup the map
    for config in configs:
        config_map[config.setting]=config.val
    # iterate through range constraints
    for knob in knobs:
        set_name = knob.set_name
        set_min = knob.min
        set_max = knob.max
        if not(config_map.has_key(set_name)):
            print "configuration does not have such setting name:"+set_name
            return False
        set_val = int(config_map[set_name])
        if set_val<set_min or set_val>set_max:
            print "configuration exeeds range"+str(set_val)+":"+str(set_min)+"->"+str(set_max)
            return False
    #iterate through and_constraints
    for and_cons in and_constraints:
        #for each and_constraint, check whether the config satisfy
        source = and_cons.source
        sink = and_cons.sink
        source_min = and_cons.source_min
        sink_min = and_cons.sink_min
        source_max = and_cons.source_max
        sink_max = and_cons.sink_max
        # now check
        if not (config_map.has_key(sink) and config_map.has_key(source)):
            # this is assume to be a valid setting
            print "cannot find sink or source in config+map"
            return True
        sink_val = config_map[sink]
        source_val = config_map[source]
        if sink_val>=sink_min and sink_val <= sink_max:
            if source_val<source_min or source_val>source_max:
                return False
    #iterate through or_constraints
        #TBD
    return True

class config:
    def __init__(self,setting,val):
        self.setting = setting
        self.val = val

class constraint:
    def __init__(self,type,source,sink,source_min,source_max,sink_min,sink_max):
        self.type = type
        self.source = source
        self.sink = sink
        self.source_min = int(source_min)
        self.source_max = int(source_max)
        self.sink_min = int(sink_min)
        self.sink_max = int(sink_max)

class knob:
    def __init__(self,svc_name,set_name,min,max):
        self.svc_name = svc_name
        self.set_name = set_name
        self.min = int(min)
        self.max = int(max)

genTrainingSet("./tmpdepfile")