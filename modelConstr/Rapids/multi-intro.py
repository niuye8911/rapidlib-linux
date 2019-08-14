from random import sample

import numpy as np
import pylab as pl
import scipy.stats as stats

slowdowns = []

for i in range(0, 3):
    slowdowns.append([])

id = 0
with open('/home/liuliu/Research/rapidlib-linux/modelConstr/source/outputs'
          '/ferret-perf-intro.csv', 'r') as f:
    for line in f:
        colums = line.split(',')
        slowdown = float(colums[1])
        slowdowns[id].append(slowdown)
        id = id + 1
        id = id % 3

data = sample(sorted(slowdowns[2]), 200)

print(len(data))
# dots

# x = range(0,len(data))
# plt.plot(x, data)
# plt.show()

# histogram
fit = stats.norm.pdf(data, np.mean(data), np.std(data))

# pl.plot(data,fit,'-o')
pl.hist(data, normed=False, bins=40, range=[1, 4])  # use this to draw
# histogram of your
# data
pl.xlabel('SlowDown', fontsize=14)
pl.ylabel('Number of Configuration', fontsize=14)
pl.show()
