from Classes import *

#read in a fact and generate a dictionary where the key is a config set, and the value is the cost
def readFact(fact_file,knobs,gt):
    fact = open(fact_file, 'r')
    if fact == None:
        print "RAPID-C / STAGE-4 : reading trained profile failed"
        return
    next(fact)#skip the first line
    for line in fact:
        col = line.split()
        knob_name = ""
        knob_val = 0.0
        cost = 0.0
        configuration = Configuration()
        for i in range(len(col)):
            if i==len(col)-1:
                cost = float(col[i])
                continue
            if col[i].isdigit():
                knob_val = int(col[i])
                configuration.addConfig([Config(knobs.getKnob(knob_name),knob_val)])
                continue
            else:
                knob_name = col[i]
        if not gt.hasEntry(configuration):
            print "cant find key"+knob_name + str(knob_val)
        gt.setCost(configuration,cost)
    print "RAPID-C / STAGE-4 : trained profile constructed"
    return