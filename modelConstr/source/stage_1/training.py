import itertools
from source.Classes import *

#stage-1 generate valid training set from constraints
def genTrainingSet(cfg_file):
    config_file = open(cfg_file, 'r') #input file
    outfile = open('trainingset','w') #output file
    # parsing the file
    knobs,and_constriants,or_constraints = processFile(config_file)
    # generate the training
    all_training, knob_samples = genAllTraining(knobs)
    # flat the all_training
    flatted = flatAll(all_training)
    # filter out the invalid configs
    flatted_all_training = []
    invalid = 0
    for config in flatted:
        if validate(config,knobs,and_constriants,or_constraints):
            # add the list to configs
            configuration = Configuration()
            configuration.addConfig(config)
            flatted_all_training.append(configuration)
            beautifyAndWriteOut(config, outfile)
        else:
            invalid+=1
    print("RAPID-C / STAGE-1 : ommited in total "+str(invalid)+" settings")
    outfile.close()
    return flatted_all_training, knob_samples

# read in a description file
def processFile(cfg_file):
    knobs = set()
    and_constriants = set()
    or_constraints = set()
    for line in cfg_file:
        col = line.split(' ')
        if len(col)==4:#knob definition
            knob_name = col[0]
            setting = col[1]
            setting_min = col[2]
            setting_max = col[3]
            knobs.add(Knob(knob_name,setting,setting_min,setting_max))
        elif len(col)==7:#it's a edge
            type = col[0]
            sink = col[1]
            source = col[2]
            source_min = col[5]
            source_max = col[6]
            sink_min = col[3]
            sink_max = col[4]
            if type=="or":
                or_constraints.add(Constraint(type,source,sink,source_min,source_max,sink_min,sink_max))
            else:
                and_constriants.add(Constraint(type,source,sink,source_min,source_max,sink_min,sink_max))
    return knobs,and_constriants,or_constraints

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
        min = int(knob.min)
        max = int(knob.max)
        step = (max-min)/9.0
        if step<1:
            step = 1
        #print "step size for "+name + "is " + str(step)
        knob_samples[name] = []
        i = min
        while i <= max:
            single_set.append(Config(name,int(i)))
            knob_samples[name].append(int(i))
            i= i + step
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

# validate if a config is valid
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

# write out to the training file
def beautifyAndWriteOut(finallist, outfile):
    for i in range(len(finallist)):
        outfile.write(finallist[i].setting + "," + str(finallist[i].val))
        if not (i == len(finallist)-1):
            outfile.write(",")
    outfile.write("\n")