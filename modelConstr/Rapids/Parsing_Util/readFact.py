from Rapids_Classes.KDG import *


def is_float(str):
    try:
        float(str)
        return True
    except ValueError:
        return False


# read in a fact and generate a dictionary where the key is a config set,
# and the value is the cost
def readFact(fact_file, knobs, gt, COST=True):
    fact = open(fact_file, 'r')
    if fact is None:
        print
        "RAPID-C / STAGE-4 : reading trained profile failed"
        return
    for line in fact:
        col = line.split()
        knob_name = ""
        knob_val = 0.0
        configuration = Configuration()
        is_digit = False
        vals = []
        for i in range(len(col)):
            if col[i].isdigit() or is_float(col[i]):
                if is_digit:
                    # this is the start of values
                    for j in range(i, len(col)):
                        vals.append(col[j])
                    break
                is_digit = True
                knob_val = int(col[i])
                configuration.addConfig(
                    [Config(knobs.getKnob(knob_name), knob_val)])
                continue
            else:
                is_digit = False
                knob_name = col[i]
        if not gt.hasEntry(configuration):
            print
            "cant find key:" + knob_name + str(knob_val)
        if COST:
            gt.setCost(configuration, float(vals[0]))
        else:
            gt.setMV(configuration, list(map(lambda x: float(x), vals)))
    print
    "RAPID-C / STAGE-4 : trained profile constructed"
    return
