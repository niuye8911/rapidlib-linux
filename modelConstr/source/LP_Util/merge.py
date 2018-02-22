import sys
from LP_Util.lp_util import *
from sets import Set

ratios=Set()

def naiveMerge(r1,r2):
    rsdg = {}
    for i in r1:
        rsdg[i] = r1[i]
    for i in r2:
        if rsdg.has_key(i):
            for j in range(0,len(rsdg[i])):
                rsdg[i][j] = rsdg[i][j]/2+r2[i][j]/2
        else:
            rsdg[i] = [n /2 for n in r2[i]]
    return rsdg

def getRSDG(r1):
    rsdgFile = open(r1,'r')
    rsdgOrig = {}
    for line in rsdgFile:
        col = line.split()
        name = col[0].split(':')[0]
        rsdgOrig[name]=[]
        rsdgOrig[name].append(float(col[0].split(":")[1]))
        for i in range (1,len(col)):
            rsdgOrig[name].append(float(col[i]))
    return rsdgOrig

def locDup(r1,r2):
    dups = {}
    for name in r1:
        if name=="err": continue
        if r2.has_key(name):
            dups[name]=True
            print "dups:"+name
    return dups

def parseMergeObserved(r1, r2, fileName):
    global ratios
    f = open(fileName,'r')
    constraints = []
    dups = locDup(r1,r2)
    print dups
    for line in f:
        constraint = ""
        col = line.split(',')
        length = len(col)
        name = ""
        lvl = -1
        for i in range(0,length):
            if i==length-1:
                constraint = constraint[:-2]
                cost = float(col[i])
                cost = str(cost)
                dualConstr = constraint
                constraint += ">= " + cost + "\n"
                dualConstr += "- " + cost + " err <= "+ cost + "\n"
                constraints.append(constraint)
                constraints.append(dualConstr)
                continue
            cur = col[i]
            if not(cur.isdigit()):#if it's service name
                name = cur
            else:
                lvl = int(cur)
                    #check if it's a dup
                if(dups.has_key(name)):
                    origVal = str(r1[name][lvl-1])
                    newVal = str(r2[name][lvl-1])
                    ratios.add(name+"@a")
                    ratios.add(name+"@b")
                    constraint += origVal + " "+ name + "@a" + " + "+newVal + " " + name+"@b " + "+ "
                    #check if it's in r1
                elif (r1.has_key(name)):
                    #constraint += str(r1[name][lvl-1]) + " 1 + "
                    constraint += str(r1[name][lvl - 1]) + " " + name + "@a + "
                    ratios.add(name + "@a")
                elif (r2.has_key(name)):
                    #constraint += str(r2[name][lvl - 1]) + " 1 + "
                    constraint += str(r2[name][lvl - 1]) + " "+name+"@b + "
                    ratios.add(name+"@b")
                else:
                    #constraint += name + "-" + str(lvl) + " + "
                    constraint += str(r1[name][lvl - 1]) + " "+name + "@a + "
                    ratios.add(name + "@a")
    return constraints

#TODO:not finished
def parseComb(rs):
    f = open(rs,'r')
    s = Set()
    for line in f:
        col = line.split('+')
        length = len(col)
        for i in range (0,length):
            if(i==length-1):
                last = col[i].split()
                s.add(last[0])
            else:
                s.add(col[i])
    return s

def genCombRS(rs1, rs2):
    s1 = parseComb(rs1)
    s2 = parseComb(rs2)
#TODO:finished

def genNewProblem(r1,r2,observed,kf1,kf2):
    #generate constraints
    constraints = parseMergeObserved(r1,r2,observed)
    prob = open("problem.lp",'w')
    prob.write("Minimize\nerr\n\n")
    # write order constraint
    prob.write("Subject To\n")
    # for s in r2:
    #     lvls = len(r2[s])
    #     for i in range(1, lvls-1):
    #         prob.write(s + "-" + str(i) + " - " + s + "-" + str(i + 1) + " > 1\n")
    # prob.write("\n")
    # for s in r1:
    #     lvls = len(r1[s])
    #     for i in range(1, lvls-1):
    #         prob.write(s + "-" + str(i) + " - " + s + "-" + str(i + 1) + " > 1\n")
    # prob.write("\n")
    # write observation constraint
    for c in constraints:
        prob.write(c)

    # write bounds
    prob.write("Bounds\n")
    # for s in r1:
    #     lvls = len(r1[s])
    #     if (lvls == 1): continue
    #     prob.write(s + "-" + str(lvls) + " = 0\n")
    # for s in r2:
    #     lvls = len(r2[s])
    #     if (lvls == 1): continue
    #     prob.write(s + "-" + str(lvls) + " = 0\n")
    for s in ratios:
        prob.write(s + " < 0.9\n")
        prob.write(s + " > 0\n")

    # write known facts
    # kf1 = parseKF(kf1)
    # kf2 = parseKF(kf2)
    # prob.write(kf1)
    # prob.write(kf2)
    prob.write("1 = 1\n")

    # write end
    prob.write("End")
    prob.close()

def genNewRSDG(r1, r2):
    #read the result
    coeff = {}
    os.system("gurobi_cl LogToConsole=0 ResultFile=coeff.sol problem.lp")
    coeffFile = open("coeff.sol",'r')
    for line in coeffFile:
        col = line.split()
        if not(len(col)==2): continue
        name = col[0]
        val = col[1]
        coeff[name] = float(val)
    #generate the new RSDG
    rsdg = {}
    for r in r1:
        name = r+"@a"
        val = r1[r]
        if coeff.has_key(name): val = [i * coeff[name] for i in val]
        rsdg[r] = val
    for r in r2:
        name = r + "@b"
        val = r2[r]
        if coeff.has_key(name): val = [i * coeff[name] for i in val]
        if rsdg.has_key(r):
            for i in range(0,len(rsdg[r])):
                rsdg[r][i]+=val[i]
        else: rsdg[r] = val
    #write RSDG to flie
    rsdgFile = open("rsdgMerge",'w')
    for i in rsdg:
        rsdgFile.write(i)
        rsdgFile.write(":")
        for v in rsdg[i]:
            rsdgFile.write(str(v))
            rsdgFile.write(" ")
        rsdgFile.write("\n")
    rsdgFile.close()
    return rsdg
