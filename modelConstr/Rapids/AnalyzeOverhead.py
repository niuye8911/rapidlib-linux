''' Analyze the overhead measured '''

import pandas as pd
import sys, os
from collections import OrderedDict
import matplotlib.pyplot as plt

APP_DIRS = ['swaptions', 'ferret', 'bodytrack', 'facedetect', 'svm', 'nn']
GRANULARITIES = list(range(1, 11)) + list(range(20, 101, 10))

APP_COLOR = {
    'swaptions': 'b',
    'ferret': 'g',
    'bodytrack': 'c',
    'svm': 'y',
    'nn': 'm',
    'facedetect': 'r'
}


def getOverheadFile(app):
    postfix = ['0.2', '0.5', '0.8']
    prefix = "/home/liuliu/Research/rapidlib-linux/modelConstr/Rapids/outputs/"
    return list(
        map(
            lambda x: prefix + app + '/overhead_report_' + app + "_" + x +
            '.csv', postfix))


def getSubDF(df, unit):
    return df.loc[df['Unit'] == unit]


def getDFAverage(subdf, col):
    return subdf[col].mean()


def genUtilization(app):
    all = []
    for f in getOverheadFile(app):
        if os.path.exists(f):
            df = pd.read_csv(f)
            all.append(df)
    df = pd.concat(all, axis=0, ignore_index=True)
    granularities = sorted(df.Unit.unique())
    utils = OrderedDict()
    for g in granularities:
        sub_df = getSubDF(df, g)
        util_col = (sub_df['Exec_Time'] / sub_df['Budget']).tolist()
        util_abs = (sub_df['Exec_Time'] - sub_df['Budget']).tolist()
        pos_util = [u for u in util_col if u < 1.05]
        over_util = [u for u in util_col if u >= 1.05]
        over_mean = 0.0 if len(
            over_util) == 0 else sum(over_util) / len(over_util)
        rc_num_col = sub_df['RC_NUM'].tolist()
        rc_budget_col = sub_df['RC_by_budget'].tolist()
        rc_num_mean = sum(rc_num_col)/len(rc_num_col)
        rc_b_mean = sum(rc_budget_col)/len(rc_budget_col)
        utils[g] = {
            'avg': sum(pos_util) / len(pos_util),
            'max': max(util_col),
            'min': min(util_col),
            'over': over_mean * float(len(over_util)) / float(len(util_col)),
            'over_num': len(over_util),
            'rc_num_mean':rc_num_mean,
            'rc_b_mean':rc_b_mean
        }
    # check the stopped granularities:
    if not len(granularities) == len(GRANULARITIES):
        last = granularities[-1]
        for g in GRANULARITIES:
            if g not in granularities:
                utils[g] = utils[last]
    return utils


def draw_over(utils):
    plt.clf()
    x_axis = list(map(lambda x: str(x), GRANULARITIES))
    datas = []
    over_nums = [0.0]*20
    for app, data in utils.items():
        over = list(map(lambda x: x['over'], data))
        over_num = list(map(lambda x: x['over_num'], data))
        datas.append(over)
        for i in range(0,len(over_num)):
            over_nums[i]+=over_num[i]
    over_cal = []
    print(over_nums)
    for i in range(0, len(GRANULARITIES)):
        over_g = list(map(lambda x: x[i], datas))
        avg_g = sum(over_g)
        over_cal.append(avg_g)
    print(over_cal)
    plt.bar(x_axis, over_cal)
    # draw the 100% limit
    #plt.plot(x_axis, full_line, 'r--', linewidth=0.3)
    plt.xlabel('Granularities')
    plt.ylabel('Budget Violation (s)')
    plt.savefig('./overhead_vio.png')

def draw_rc_num(utils):
    plt.clf()
    x_axis = list(map(lambda x: str(x), GRANULARITIES))
    datas = []
    fig,ax = plt.subplots(nrows = 1, ncols = 2)
    ax0 = ax[0]
    ax1=ax[1]
    ax0.axis(ymin=0,ymax=40)
    ax1.axis(ymin=0,ymax=40)
    for app, data in utils.items():
        rc_num = list(map(lambda x: x['rc_num_mean'], data))
        rc_b = list(map(lambda x: x['rc_b_mean'], data))
        ax0.plot(x_axis, rc_b, APP_COLOR[app],linewidth=1)
        ax1.plot(x_axis, rc_num,APP_COLOR[app],label=app,linewidth=1)

    # draw the 100% limit
    #plt.plot(x_axis, full_line, 'r--', linewidth=0.3)
    #ax.xlabel('Monitor Frequency', fontsize=16)
    #ax.ylim((0,40))
    #ax.ylabel('Performed Reconfiguration', fontsize=16)
    ax1.legend(loc='upper right',
               bbox_to_anchor=(1.0, 1.0),
               ncol=1,
               prop={'size': 10},
               frameon=False)
    plt.setp(ax0.xaxis.get_majorticklabels(),rotation=90)
    plt.setp(ax1.xaxis.get_majorticklabels(),rotation=90)
    ax0.set_title('After Budget Optimization')
    ax1.set_title('After Config Optimization')
    fig.text(0.5,0.01, 'Monitor Frequency',ha='center',size=15)
    fig.text(0.01,0.5, 'Performed Reconfiguration',rotation=90,va='center',size=15)
    fig.savefig('./overhead_rc.png')

def draw_util(utils):
    x_axis = list(map(lambda x: str(x), GRANULARITIES))
    #full_line = [1.0] * len(x_axis)
    for app, data in utils.items():
        avg = list(map(lambda x: x['avg'], data))
        max = list(map(lambda x: x['max'], data))
        min = list(map(lambda x: x['min'], data))
        #max_d = [(i - j) if i>1.05 else 0.0 for i, j in zip(max, avg)]
        #min_d = [j - i for i, j in zip(min, avg)]
        #min_d = [0.0]*len(min)
        #yerr = [min_d, max_d]
        plt.errorbar(
            x_axis,
            avg,
            color=APP_COLOR[app],
            #yerr=yerr,
            #elinewidth=0.5,
            label=app)
    # draw the 100% limit
    #plt.plot(x_axis, full_line, 'r--', linewidth=0.3)
    plt.xlabel('Monitor Frequency', fontsize=16)
    plt.ylabel('Budget Utilization', fontsize=16)
    plt.legend(loc='upper center',
               bbox_to_anchor=(0.5, 1.15),
               ncol=3,
               prop={'size': 16})
    plt.savefig('./overhead.png')


def main(argv):
    # analyze utilization
    utils = OrderedDict()
    for app in APP_DIRS:
        util_app = genUtilization(app)
        utils[app] = util_app.values()
    #draw_util(utils)
    #draw_over(utils)
    draw_rc_num(utils)

    # analyze the number of reconfiguration


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
