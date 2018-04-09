#read in a fact and generate a dictionary where the key is a config set, and the value is the cost
def readFact(fact):
    final_profile = {}
    for line in fact:
        col = line.split(',')
        knob_name = ""
        knob_val = 0.0
        config_name = ""
        cost = 0.0
        for i in range(len(col)):
            if i==len(col)-1:
                cost = float(col[i])
                continue
            knob_name = col[i]
            knob_val = float(col[i+1])
            config_name+=knob_name+","+str(knob_val)
            i+=1
        final_profile[config_name] = cost
    return final_profile