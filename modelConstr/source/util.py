# A utility file providing all helper functions

import numpy as np,numpy.linalg

def checkRate(rsdg,fact):
    factCost = open(fact,'r')
    report = open("outputs/report",'w')
    meanErr = 0.0
    maxErr = 0.0
    maxId = -1
    TotErr = 0.0
    TotConfig = 0
    lineNum = 0
    for line in factCost:
        lineNum+=1
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
                err = abs((gtV-estV)/gtV)
                report.write("%f,%f,err:%f\n" % (gtV , estV, err))
                TotErr += err
                if err >= maxErr : maxId = lineNum
                maxErr = max(maxErr,err)
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
                    estV += rsdg[name][lvl-1]
                else:
                    estV += rsdg[name][0]
    print TotErr
    print TotConfig
    meanErr = TotErr/TotConfig
    report.write("Mean:"+str(meanErr))
    report.close()
    return [meanErr,maxErr, maxId]

def checkAccuracy(fact,app,observed):
    pass
 #   if app=="ferret":
 ##       checkFerretWrapper(fact, observed)
  #  elif app == "swaptions":
  #      checkSwaptionWrapper(fact, observed)
  #  elif app == "bodytrack":
  #      checkBodytrackWrapper(fact, observed)