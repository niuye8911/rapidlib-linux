import itertools
from Classes import *

CONTINUOUS = 'C'
DISCRETE = 'D'
DELIMITER = ' '
AND_SEC = 'AND'
OR_SEC = 'OR'
VALID_CONSTRAINT_LENGTH = 4

# determine if a line is valid
def isConstraint(line):
    return len(line.split(DELIMITER)) == VALID_CONSTRAINT_LENGTH and line.split(DELIMITER)[2]!="=>"

def isANDLine(line):
    return line.startswith(AND_SEC)

def isORLine(line):
    return line.startswith(OR_SEC)

def isEdge(line):
    col = line.split(DELIMITER)
    return len(col)>=4 and col[2]=="=>"

#stage_1 generate valid training set from constraints
def genTrainingSet(cfg_file):
    print "RAPID-C / STAGE-1.1 : generating... training set in file ./trainingset"
    config_file = open(cfg_file, 'r') #input file
    # parsing the file
    appname,knobs,and_constriants,or_constraints = processFile(config_file)
    # generate the training
    all_training, knob_samples = genAllTraining(knobs)
    # flat the all_training
    flatted = flatAll(all_training)
    # filter out the invalid configs
    flatted_all_training = Profile()
    invalid = 0
    for config in flatted:
        if validate(config,knobs,and_constriants,or_constraints):
            # add the list to configs
            configuration = Configuration()
            configuration.addConfig(config)
            flatted_all_training.addCostEntry(configuration, 0.0)
        else:
            invalid+=1
    print("RAPID-C / STAGE-1 : ommited in total "+str(invalid)+" settings")
    # write all valid configs to file
    outfile = open('./outputs/trainingset', 'w')  # output file
    beautifyAndWriteOut(flatted_all_training,outfile)
    outfile.close()
    # prepare a Knobs
    knobs_class = Knobs()
    for k in knobs:
        knobs_class.addKnob(k)
    return appname,knobs_class,flatted_all_training, knob_samples,and_constriants,or_constraints,knobs

# read in a description file
def processFile(cfg_file):
    appname = ""
    knobs = set()
    and_edges = set()
    or_edges = set()
    and_sec = False
    or_sec = False
    for line in cfg_file:
        col = line.split(' ')
        if appname=="": #first line
            appname= col[0]
        elif isANDLine(line):
            and_sec = True
            or_sec = False
        elif isORLine(line):
            and_sec = False
            or_sec = True
        elif isConstraint(line):
            svcName = col[0]
            setName = col[1]
            if(col[2]==CONTINUOUS):
                min = getMinMax(col[3])['min']
                max = getMinMax(col[3])['max']
                knobs.add(Knob_C(svcName,setName).setRange(min,max))
            elif(col[2]==DISCRETE):
                values = getValues(col[3])
                knobs.add(Knob_D(svcName,setName).setValues(values))
        elif isEdge(line):#it's a edge
            sinkSvc = col[0]
            sinkValue = getValues(col[1]) if col[1][0]=='{' else getMinMax(col[1])
            if and_sec:
                sourceSvc = col[3]
                sourceValue = getValues(col[4]) if col[4][0]=='{' else getMinMax(col[4])
                and_edges.add(AndConstraint(sourceSvc, sinkSvc,sourceValue,sinkValue))
            elif or_sec:
                sources = {}
                source_list = col[3].split('/')
                for ele in source_list:
                    if len(ele.split('{'))==2:
                        name,values = ele.split('{')
                        values="{"+values
                        sources[name] = getValues(values)
                    else:
                        name,values = ele.split('[')
                        values="["+values
                        sources[name] = getMinMax(values)
                or_edges.add(OrConstraint(sinkSvc, sinkValue,sources))
    return appname,knobs,and_edges,or_edges

# getMinMax
def getMinMax(line):
    length = len(line)
    if line[0]!='[':
        return {'min':None,"max":None}
    line = line[1:-2] if line[length-1]=="\n" else line[1:-1] # remove brackets
    return {'min':int(line.split(',')[0]), 'max':int(line.split(',')[1])}


def getValues(line):
    length = len(line)
    if line[0]!='{':
        return None
    line = line[1:-2] if line[length-1]=="\n" else line[1:-1] # remove brackets
    result = []
    values = line.split(',')
    for value in values:
        result.append(int(value))
    return result

# flat a single tuple
def flat(tup,finallist):
    if type(tup) is tuple:
        if (len(tup)==0):
            return
        flat(tup[0],finallist)
        flat(tup[1:],finallist)
    else:
        finallist.append(tup)

# flatten a list of tuples
def flatAll(listOfTuples):
    result = []
    for t in listOfTuples:
        tmp_result = []
        flat(t,tmp_result)
        result.append(tmp_result)
    return result

# generate all possible combinations given a set of knobs
# return:
# product - a cross product containing bunch of Configurations
# knob_samples - a disctionary contains all sampled configs
def genAllTraining(knobs):
    final_sets = set()
    knob_samples = {}
    for knob in knobs:
        single_set = []
        name = knob.set_name
        knob_samples[name] = []
        if knob.isContinuous():#continuous knob
            min = knob.min
            max = knob.max
            step = (max-min)/3.0
            if step<1:
                step = 1
            #print "step size for "+name + "is " + str(step)
            i = min
            single_set.append(Config(knob, i))
            knob_samples[name].append(i)
            while i < max:
                i = i + step
                if i+step > max:
                    i = max
                single_set.append(Config(knob,int(i))) # right now support INT
                knob_samples[name].append(int(i))
        else:# discrete knobs
            # all settings will be included
            for value in knob.values:
                single_set.append(Config(knob,value))
                knob_samples[name].append(int(value))
        frozen_single = frozenset(single_set)
        final_sets.add(frozen_single)
    product = crossproduct(final_sets)
    return product, knob_samples

# do a cross product of a set of configuration lists
def crossproduct(final_sets):
    pro = {}
    inited = False;
    for i in final_sets:
        if inited:
            pro = itertools.product(pro, i)
        else:
            # print "init pro"
            pro = i
            inited = True
    return pro

# validate if a combination of configs is valid
def validate(configs,knobs,and_constraints,or_constraints):
    config_map = dict()
    # setup the map
    for config in configs:
        config_map[config.knob.set_name]=config.val
    # iterate through range constraints
    for knob in knobs:
        set_name = knob.set_name
        if not(config_map.has_key(set_name)):
            print "configuration misses this setting name:"+set_name
            return False
        set_val = config_map[set_name]
        if not knob.hasValue(set_val):
            print "config not valid: "+set_name+"="+str(set_val)
            return False
    #iterate through and_constraints
    for and_cons in and_constraints:
        #for each and_constraint, check whether the config satisfy
        source = and_cons.source
        sink = and_cons.sink
        sink_values = and_cons.sink_value
        source_val = config_map[source]
        sink_val = config_map[sink]
        # now check
        if not (config_map.has_key(sink) and config_map.has_key(source)):
            # this is assume to be a valid setting
            print "cannot find sink or source in config_map:"+sink+":"+source
            continue
        if not and_cons.valid(source_val,sink_val):
            return False
    #iterate through or_constraints
    for or_cons in or_constraints:
        sources = or_cons.sources
        sink = and_cons.sink
        sink_values = and_cons.sink_value
        sink_val = config_map[sink]
        # now check
        if not (config_map.has_key(sink)):
            # this is assume to be a valid setting
            print "cannot find sink or source in config_map:"+sink
            continue
        source_dict = {}
        for source in sources:
            source_val = config_map[source]
            source_dict[source] = source_val
        if not or_cons.valid(source_dict,sink_val):
            return False
    return True

# write out to the training file
def beautifyAndWriteOut(empty_profile, outfile):
    output_buffer = set()
    flatted_configurations = empty_profile.profile_table
    for configuration_string in flatted_configurations:
        #config_list = configuration.retrieve_configs()
        #tmp_output = ""
        #for i in range(len(config_list)):
        #    tmp_output+=config_list[i].knob.set_name + "," + str(config_list[i].val)
        #    if not (i == len(config_list)-1):
        #        tmp_output+=","
        output_buffer.add(configuration_string)
    for o in sorted(output_buffer):
        outfile.write(o)
        outfile.write("\n")
