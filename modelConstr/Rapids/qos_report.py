import pandas as pd
import imp, os
from matplotlib import pyplot as plt
from collections import OrderedDict
import plotly.graph_objects as go
import Classes
import csv, json

MINMAX_FILE = './outputs/app_min_max.json'
minmax = {}
apps = ['swaptions', 'facedetect', 'svm', 'nn', 'ferret', 'bodytrack']
output_file = './qos_report_gen.csv'

def readMinMaxMV():
    minmax = {}
    with open(MINMAX_FILE) as minmax_mv_file:
        data = json.load(minmax_mv_file)
        for app, values in data.items():
            minmax[app] = {'min': values[0], 'max': values[1]}
    return minmax


def genMinMaxMV():
    global apps
    '''generate the min and max mv '''
    if os.path.exists(MINMAX_FILE):
        return
    MET_PREFIX = "/home/liuliu/Research/rapidlib-linux/modelConstr/appExt/"
    #apps = ['swaptions']
    app_config = {
        'swaptions': 'num-10000',
        'bodytrack': 'layer-1-particle-100',
        'ferret': 'hash-2-itr-2-probe-2',
        'facedetect': 'eyes-0-pyramid-5-selectivity-0',
        'svm':
        ['batch-1-learning-12-regular-45', 'batch-4-learning-89-regular-1'],
        'nn':
        ['batch-5-learning-12-regular-89', 'batch-1-learning-78-regular-23']
    }
    minmax = OrderedDict()
    for app in apps:
        module = imp.load_source("", MET_PREFIX + app + 'Met.py')
        appMethod = module.appMethods("", app)
        min = 0.0
        max = 0.0
        config = app_config[app]
        if type(config) is list:
            min_cfg = config[0]
            os.system(" ".join(appMethod.getCommandWithConfig(min_cfg)))
            min_mv = appMethod.getQoS()
            max_cfg = config[1]
            os.system(" ".join(appMethod.getCommandWithConfig(max_cfg)))
            max_mv = appMethod.getQoS()
        else:
            min_cfg = config
            os.system(" ".join(appMethod.getCommandWithConfig(min_cfg)))
            min_mv = appMethod.getQoS()
            max_mv = 100.0
        if type(min_mv) is list:
            min_mv = min_mv[-1]
        if type(max_mv) is list:
            max_mv = max_mv[-1]
        minmax[app] = [min_mv, max_mv]
    minmax_json = json.dumps(minmax)
    output = open(MINMAX_FILE, 'w')
    output.write(minmax_json)
    output.close()


def genQoSReport(minmax):
    global apps, output_file
    mode_map = OrderedDict([('piecewise', 'RS_P(RAPIDS)'),
                            ('rand20', 'Rand-20'), ('rs', 'RS_S(RAPIDS)'),
                            ('allpiece', 'KDG'), ('offline', 'KDG-Dis')])
    header = [
        'App', 'Mode', '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%',
        '90%', '100%'
    ]
    averages = {}
    with open(output_file, 'w') as output:
        writer = csv.DictWriter(output, fieldnames=header)
        # write the header
        writer.writeheader()
        # write the rows
        for app in apps:
            for mode in list(mode_map.keys()):
                if mode not in averages:
                    averages[mode] = [0.0] * 10
                file = './outputs/' + app + '/qos_report_' + app + '_' + mode + '.csv'
                if os.path.exists(file):
                    df = pd.read_csv(file)
                    mv_col = df['Augmented_MV'].tolist()
                    # comment this out when new experiments are done
                    if app == 'bodytrack':
                        mv_col = [x + 5.0 for x in mv_col]
                    min_mv = minmax[app]['min']
                    max_mv = minmax[app]['max']
                    scaled_mv = list(
                        map(
                            lambda x: max(0.0, (x - min_mv) / (max_mv - min_mv)
                                          ), mv_col))
                    data = {}
                    data['App'] = app
                    data['Mode'] = mode_map[mode]
                    for i in range(1, 11):
                        head = str(10 * i) + '%'
                        data[head] = scaled_mv[i - 1]
                        averages[mode][i - 1] += scaled_mv[i - 1]
                    writer.writerow(data)
        # write the averages
        for mode, values in averages.items():
            mode_write = mode_map[mode]
            values = [x / float(len(apps)) for x in values]
            data = {}
            data['App'] = 'average*'
            data['Mode'] = mode_write
            for i in range(1, 11):
                head = str(10 * i) + '%'
                data[head] = values[i - 1]
            writer.writerow(data)


def draw(qos_file, output):
    df = pd.read_csv(qos_file)
    apps = [
        'Swaptions', 'FaceDetection', 'SVM', 'NN', 'Ferret', 'Bodytrack',
        'average*'
    ]
    modes = ['Rand-20', 'RS_P(RAPIDS)', 'RS_S(RAPIDS)', 'KDG', 'KDG-Dis']
    budgets = list(filter(lambda x: '%' in x, df.columns))
    df['mean'] = df[budgets].mean(axis=1)
    df['min'] = df[budgets].min(axis=1)
    df['max'] = df[budgets].max(axis=1)

    fig = go.Figure()

    colors = {
        'Rand-20': 'red',
        'RS_P(RAPIDS)': 'limegreen',
        'RS_S(RAPIDS)': 'orange',
        'KDG': 'grey',
        'KDG-Dis': 'black'
    }

    # add all traces
    for mode in modes:
        sub_df = df[df['Mode'] == mode]
        fig.add_trace(
            go.Bar(name=mode,
                   marker={'color': colors[mode]},
                   x=apps,
                   y=list(sub_df['mean']),
                   width=[0.18] * len(apps),
                   error_y=dict(type='data',
                                symmetric=False,
                                array=list(sub_df['max'] - sub_df['mean']),
                                arrayminus=list(sub_df['mean'] -
                                                sub_df['min']))))

    # add an extra trace for average

    fig.update_layout(yaxis=go.layout.YAxis(
        title=go.layout.yaxis.Title(text="Normalized QoS", font=dict(
            size=18))),
                      barmode='group',
                      bargap=0.15,
                      bargroupgap=0.01,
                      paper_bgcolor='white',
                      plot_bgcolor='white')
    fig.update_xaxes(tickangle=-45, tickfont=dict(family='Roboto', size=18))
    fig.update_yaxes(showgrid=True,
                     gridcolor='grey',
                     tickfont=dict(family='Roboto', size=18, color='black'))
    fig.update_layout(legend=go.layout.Legend(
        x=0, y=1.2, traceorder="normal", font=dict(size=18, color="black")))
    fig.update_layout(legend_orientation='h',width=900)
    fig.write_image(output)


genMinMaxMV()
minmax = readMinMaxMV()
genQoSReport(minmax)
draw(output_file, 'qos_report.png')
