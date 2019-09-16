import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from collections import OrderedDict
import sys

APPS = ['swaptions', 'ferret', 'bodytrack', 'facedetect', 'svm', 'nn']
APP_COLOR = {
    'swaptions': 'b',
    'ferret': 'g',
    'bodytrack': 'c',
    'svm': 'y',
    'nn': 'm',
    'facedetect': 'r'
}

def getFileName(app):
    return 'input_' + app + '_log.txt'


def getInputValues(file):
    values = []
    with open(file) as f:
        for line in f:
            value = line.split(' ')[:-1]
            value = [float(x) for x in value]
    values = values + value
    return values


def draw_input(values):
    plt.clf()
    for app, value in values.items():
        # normalize the data
        #norm_data = [(x - min(value)) / (max(value) - min(value))
        #             for x in value]
        value.sort()
        data_mean = np.mean(value)
        data_std = np.std(value)
        print(app,data_mean,data_std)
        pdf = stats.norm.pdf(value, data_mean,data_std)
        plt.plot(value, pdf, APP_COLOR[app], label=app)
    plt.xlabel('Input Cost Range')
    plt.ylabel('Probability Density')
    plt.legend(loc='upper center',
               bbox_to_anchor=(0.5, 1.15),
               ncol=3,
               prop={'size': 10})
    plt.savefig('./input_dense.png')


def main(argv):
    # analyze input distribution
    values = OrderedDict()
    for app in APPS:
        input_file = getFileName(app)
        values[app] = getInputValues(input_file)
    draw_input(values)

    # analyze the number of reconfiguration


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
