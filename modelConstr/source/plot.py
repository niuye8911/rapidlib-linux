import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as pl
import scipy as sp
import pylab

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
    #pl.hist(data, bins=40, range=[-1,1],normed=True, color='grey')

    #fig = pl.plot
    hist, bins = np.histogram(data,bins=50,range=[-0.3,0.3],density=1)
    pl.ylim(0.0,0.25)
    p1 = pl.bar(bins[:-1], hist.astype(np.float32) / hist.sum(), width=(bins[1] - bins[0]), color='blue')
    #p1.set_xlabel('Smarts')
    pl.legend([p1], ["Ferret-PWL"],fontsize=12,loc='upper right')
    pylab.xlabel("Relative Error",fontsize=16)
    pylab.ylabel("Percentage (%)",fontsize=16)

    # print the mean / std / confidence interval
    m,m_1,m_2 = mean_confidence_interval(data)
    print m, m_1, m_2,np.std(data)

    #stats.probplot(data, dist="norm", plot=pylab)
    #pylab.show()
    # kde = stats.gaussian_kde(data)
    # length = len(data)
    # xx = np.linspace(min,max,length)
    #pl.hist(data,bins=50,normed=1)      #use this to draw histogram of your data
    # results, edges = np.histogram(data, bins = 40, range=[-1,1], normed=True)
    # binWidth = edges[1] - edges[0]
    # pl.bar(edges[:-1], results * binWidth, binWidth)
    # #pl.plot(xx, kde(xx))
    # pl.show()

    pl.show()

def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), stats.sem(a)
    h = se * sp.stats.t._ppf((1 + confidence) / 2., n - 1)
    return m, m - h, m + h