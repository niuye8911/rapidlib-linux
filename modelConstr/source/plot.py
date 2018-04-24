import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as pl

def draw(datafile):
    data = []
    d = open(datafile,'r')
    min = 1
    max = -1
    for line in d:
        col = line.split(",")
        length = len(col)
        err = float(col[length-1][:-1])
        if err > max:
            max = err
        if err<min:
            min = err
        data.append(float(err))
    data = sorted(data)
    print data
    kde = stats.gaussian_kde(data)
    length = len(data)
    xx = np.linspace(min,max,length)
    pl.hist(data,bins=100)      #use this to draw histogram of your data
    pl.plot(xx,kde(xx))
    pl.show()
