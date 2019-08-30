import pandas as pd
from matplotlib import pyplot as plt
import plotly.graph_objects as go


def draw(qos_file, output):
    df = pd.read_csv(qos_file)
    apps = ['Swaptions','FaceDetection','SVM','NN','Ferret','Bodytrack','average*']
    modes = ['Rand-20', 'RS_P(RAPIDS)', 'RS_S(RAPIDS)','KDG','KDG-Dis']
    budgets = list(filter(lambda x: '%' in x, df.columns))
    df['mean'] = df[budgets].mean(axis=1)
    df['min'] = df[budgets].min(axis=1)
    df['max'] = df[budgets].max(axis=1)

    fig = go.Figure()

    colors = {'Rand-20': 'red', 'RS_P(RAPIDS)': 'limegreen', 'RS_S(RAPIDS)': 'orange', 'KDG':'grey', 'KDG-Dis':'black'}

    # add all traces
    for mode in modes:
        sub_df = df[df['Mode'] == mode]
        fig.add_trace(
            go.Bar(name=mode,
                   marker={'color': colors[mode]},
                   x=apps,
                   y=list(sub_df['mean']),
                   width=[0.15]*len(apps),
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
                      bargap=0.25,
                      bargroupgap=1,
                      paper_bgcolor='white',
                      plot_bgcolor='white')
    fig.update_xaxes(tickangle=-45, tickfont=dict(family='Roboto', size=18))
    fig.update_yaxes(showgrid=True,
                     gridcolor='grey',
                     tickfont=dict(family='Roboto', size=18, color='black'))
    fig.update_layout(legend=go.layout.Legend(
        x=0, y=1.1, traceorder="normal", font=dict(size=20, color="black")))
    fig.update_layout(legend_orientation='h')
    fig.show()


draw('./qos_report.csv', 'qos_report.png')
