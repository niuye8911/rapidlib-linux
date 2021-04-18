from Rapids_Classes.KDG import *
import re

CONT_SECTION = "<Continuous Knobs>:"
DISC_SECTION = "<Discrete Knobs>:"
DEP_SECTION = "<Dependencies>:"
METRIC_SECTION = "<Sub-Metrics>:"

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


# read in a description file
def readDesc(desc_file):
    knobs = set()
    and_constraints = set()
    or_constraints = set()
    desc = open(desc_file, 'r')
    section = 0
    for line in desc:
        print(line)
        if CONT_SECTION in line:
            section = 0
            continue
        elif DISC_SECTION in line:
            section = 1
            continue
        elif DEP_SECTION in line:
            section = 2
            continue
        elif METRIC_SECTION in line:
            section = 3
            continue
        else:
            # section lines
            line = line.strip()
            col = line.split(' ')
            if section == 0:  # continuous knobs
                setting_name = col[0]
                knob_name = setting_name + "Num"
                regex = re.compile('[0-9]+')
                setting_min, setting_max = regex.findall(col[1])
                ktype = col[2]
                knobs.add(Knob(knob_name, setting_name, setting_min, setting_max))
            elif section == 1:  # discrete knobs
                setting_name = col[0]
                knob_name = setting_name + "Num"
                regex = re.compile('[0-9]+')
                vals = regex.findall(col[1])
                ktype = col[2]
                k = Knob(knob_name, setting_name, min(vals), max(vals))
                k.setValues(vals)
                knobs.add(k)
            elif section == 2:  # deps
                dtype = col[0][0:-1].lower()
                sink = col[1]
                # sink
                regex = re.compile('[0-9]+')
                sink_vals = regex.findall(col[2])
                if len(sink_vals) == 2:
                    # cont sink
                    sink_min = sink_vals[0]
                    sink_max = sink_vals[1]
                else:
                    sink_min = sink_vals[0]
                    sink_max = sink_vals[0]
                # source
                sources = " ".join(col[4:])
                sources_col = sources.split(',')
                if len(sources_col) == 1:
                    dtype = "and"
                for source_col in sources_col:
                    source_col = source_col.strip()
                    source = source_col.split(" ")[0]
                    if '{' in source_col.split(" ")[1]:
                        # discrete
                        vals = regex.findall(source_col.split(" ")[1])
                        for val in vals:
                            if dtype == "and":
                                and_constraints.add(Constraint(dtype, source, sink, val, val,
                                                               sink_min, sink_max))
                            else:
                                or_constraints.add(Constraint(dtype, source, sink, val, val,
                                                              sink_min, sink_max))
                    else:
                        # continue
                        vals = regex.findall(source_col.split(" ")[1])
                        if dtype == "and":
                            and_constraints.add(Constraint(dtype, source, sink, vals[0], vals[1],
                                                           sink_min, sink_max))
                        else:
                            or_constraints.add(Constraint(dtype, source, sink, vals[0], vals[1],
                                                          sink_min, sink_max))

    return knobs, and_constraints, or_constraints
