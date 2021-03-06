# A utility file providing all helper functions
from shutil import copyfile
import os

def __get_minmax(file):
    min_v = 999999.0
    max_v = -999999.0
    with open(file, 'r') as f:
        for line in f:
            col = line.rstrip().split(' ')
            v = float(col[-1])
            min_v = min(min_v, v)
            max_v = max(max_v, v)
    return min_v, max_v


def updateAppMinMax(appInfo, appMethod):
    cost_file = appInfo.FILE_PATHS['COST_FILE_PATH']
    mv_file = appInfo.FILE_PATHS['MV_FILE_PATH']
    if os.path.exists(cost_file):
        min_cost, max_cost = __get_minmax(cost_file)
        appMethod.min_cost = min_cost
        appMethod.max_cost = max_cost
    if os.path.exists(mv_file):
        min_mv, max_mv = __get_minmax(mv_file)
        appMethod.min_mv = min_mv
        appMethod.max_mv = max_mv

def recoverTimeRecord(appInfo, units):
    ''' estimate the total training time from a trained cost profile '''
    time_record = {}
    with open(appInfo.FILE_PATHS['COST_FILE_PATH'], 'r') as costfile:
        for line in costfile:
            col = line.split()
            unit_cost = col[-1]
            configs = []
            config_part = col[0:-1]
            for i in range(0, len(config_part) - 1, 2):
                name = config_part[i]
                val = config_part[i + 1]
                configs.append(name + "-" + val)
            config = "-".join(sorted(configs))
            time_record[config] = float(unit_cost) * units
    return time_record


def genOfflineFact(app_name):
    dir = 'outputs/' + app_name + "/"
    cost_fact = dir + app_name + '-cost.fact'
    mv_fact = dir + app_name + '-mv.fact'
    copyfile(cost_fact, './factcost.csv')
    copyfile(mv_fact, './factmv.csv')


def checkRate(rsdg, fact):
    factCost = open(fact, 'r')
    report = open("outputs/report", 'w')
    meanErr = 0.0
    maxErr = 0.0
    maxId = -1
    TotErr = 0.0
    TotConfig = 0
    lineNum = 0
    for line in factCost:
        lineNum += 1
        col = line.split(',')
        length = len(col)
        name = ""
        lvl = -1
        gtV = -1
        estV = 0
        TotConfig += 1
        for i in range(0, length):
            if i == length - 1:
                gtV = float(col[i])
                err = abs((gtV - estV) / gtV)
                report.write("%f,%f,err:%f\n" % (gtV, estV, err))
                TotErr += err
                if err >= maxErr: maxId = lineNum
                maxErr = max(maxErr, err)
                # the line below caused the calculation error
                TotConfig += 1
                estV = 0
                continue
            cur = col[i]
            # write the current element to file
            report.write(cur)
            report.write(",")
            if not (cur.isdigit()):  # if it's service name
                name = cur
            else:
                lvl = int(cur)
                if not (lvl == 0):
                    estV += rsdg[name][lvl - 1]
                else:
                    estV += rsdg[name][0]
    print
    TotErr
    print
    TotConfig
    meanErr = TotErr / TotConfig
    report.write("Mean:" + str(meanErr))
    report.close()
    return [meanErr, maxErr, maxId]


def checkAccuracy(fact, app, observed):
    pass


#   if app=="ferret":
##       checkFerretWrapper(fact, observed)
#  elif app == "swaptions":
#      checkSwaptionWrapper(fact, observed)
#  elif app == "bodytrack":
#      checkBodytrackWrapper(fact, observed)
