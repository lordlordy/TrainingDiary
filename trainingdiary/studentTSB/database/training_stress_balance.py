import os
import matplotlib
import datetime
# this is to prevent trying to show window with image.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from django.conf import settings

CTL_DECAY_DAYS = 42
CTL_IMPACT_DAYS = 42
ATL_DECAY_DAYS = 7
ATL_IMPACT_DAYS = 7
CTL_DECAY = np.exp(-1 / CTL_DECAY_DAYS)
CTL_IMPACT = 1 - np.exp(-1 / CTL_IMPACT_DAYS)
ATL_DECAY = np.exp(-1 / ATL_DECAY_DAYS)
ATL_IMPACT = 1 - np.exp(-1 / ATL_IMPACT_DAYS)


def tsb_time_series(date_value_pairs):
    """

    :param date_value_pairs: list: [(Date, Double)]
    :return:
    """
    dates = [d[0] for d in date_value_pairs]
    current_date = min(dates)
    last_date = max(dates)
    tss_dict = dict()
    for d in date_value_pairs:
        tss_dict[d[0]] = d[1]

    atl = ctl = 0.0
    result = []

    while current_date <= last_date:
        tss = 0.0
        if current_date in tss_dict:
            tss = tss_dict[current_date]
        ctl = tss * CTL_IMPACT + ctl * CTL_DECAY
        atl = tss * ATL_IMPACT + atl * ATL_DECAY
        result.append((current_date, (atl, ctl, ctl-atl, tss)))
        current_date = current_date + datetime.timedelta(days=1)
        current_date = current_date

    return result


def combine_date_value_arrays(data_value_arrays):
    """

    :param data_value_arrays: array of date value pairs: [[Date, Double]]
    :return:
    """
    tss_dict = dict()
    for pairs in data_value_arrays:
        for pair in pairs:
            tss_dict[pair[0]] = tss_dict.get(pair[0], 0.0) + pair[1]

    return tss_dict.items()


def tsb_for_player(player, file_name):
    tsb_ts = tsb_time_series(player.tss_time_series)
    graphs = graphs_for_tss_time_series(tsb_ts)
    save_image(graphs, file_name)


def tsb_for_team(team, file_name):
    tsb_ts = tsb_time_series(team.tss_time_series)
    graphs = graphs_for_tss_time_series(tsb_ts)
    save_image(graphs, file_name)


def graphs_for_tss_time_series(tss_ts):
    atl = [[i[0], i[1][0]] for i in tss_ts]
    ctl = [[i[0], i[1][1]] for i in tss_ts]
    tsb = [[i[0], i[1][2]] for i in tss_ts]
    tss = [[i[0], i[1][3]] for i in tss_ts]
    from . import Graph
    graphs = list()
    graphs.append(Graph('ATL', atl))
    graphs.append(Graph('CTL', ctl))
    graphs.append(Graph('TSB', tsb, **{Graph.TYPE: Graph.T_FILL}))
    graphs.append(Graph('TSS', tss, **{Graph.TYPE: Graph.T_POINT, Graph.AXIS: Graph.AXIS_SECONDARY, Graph.SIZE: 6,
                                       Graph.PLOT_ZEROES: False}))
    return graphs


def save_image(graphs, file_name, colour_map='rainbow', background='whitesmoke',
               from_date=datetime.date(2000,1,1), to_date=datetime.date(2020,1,1)):

    fig = plt.figure(figsize=[24, 13.5])
    ax_primary = fig.gca()
    ax_secondary = ax_primary.twinx()
    ax_primary.grid()

    i = 0
    color_idx = np.linspace(0, 1, len(graphs))
    c_map = plt.get_cmap(colour_map)

    for graph in graphs:
        time_series = graph.time_series
        name = graph.name
        time_series = time_series.loc[from_date:to_date]
        if len(time_series) == 0:
            # means no data in range provided
            continue
        ax = ax_primary
        if graph.is_secondary():
            ax = ax_secondary
        if graph.is_bar():
            test = (max(time_series.index.values) - min(time_series.index.values)) / (24 * 60 * 60 * 1000000000)
            width = -float(test) / len(time_series.values)
            ax.bar(time_series.index.values, time_series.values, label=name, color=c_map(color_idx[i]),
                   align='edge', width=width, alpha=0.5)
        elif graph.is_histogram():
            min_x = np.nanmin(time_series.values)
            max_x = np.nanmax(time_series.values)
            x_width = (max_x - min_x) / graph.size()
            # to avoid plotting loads of zeroes
            increment = 0
            if graph.is_day_not_rolling():
                increment = 0.01
            xbins = np.arange(min_x + increment, max_x + x_width, x_width)

            ax.hist(time_series.values, bins=xbins, color=c_map(color_idx[i]))
        else:
            ax.plot(time_series, color=c_map(color_idx[i]), label=name, linewidth=graph.size(),
                    markersize=graph.size(), linestyle=graph.line_style(), marker=graph.marker())
            if graph.is_fill():
                try:
                    ax.fill_between(time_series.index.values, 0, time_series.values, color=c_map(color_idx[i]), alpha=0.5)
                except TypeError as e:
                    print(e)

        i += 1

    ax_primary.set_facecolor(background)
    ax_primary.legend(loc=2)
    ax_secondary.legend(loc=1)
    fig.savefig(os.path.join(settings.BASE_DIR, f'workoutentry/static/tmp/{file_name}'), bbox_inches='tight')
    plt.close(fig)
