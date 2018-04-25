import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as pl
import pylab
import seaborn as sns

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
    #sns.distplot(data,norm_hist=True,KDE=False)
    #pl.hist(data, normed=True, color='grey')


    #hist, bins = np.histogram(data)
    #pl.bar(bins[:-1], hist.astype(np.float32) / hist.sum(), width=(bins[1] - bins[0]), color='grey')
    stats.probplot(data, dist="norm", plot=pylab)
    pylab.show()
    # kde = stats.gaussian_kde(data)
    # length = len(data)
    # xx = np.linspace(min,max,length)
    # #pl.hist(data,bins=100,normed=1)      #use this to draw histogram of your data
    # results, edges = np.histogram(data, bins = 40, range=[-1,1], normed=True)
    # binWidth = edges[1] - edges[0]
    # pl.bar(edges[:-1], results * binWidth, binWidth)
    # #pl.plot(xx, kde(xx))
    # pl.show()

    pl.show()