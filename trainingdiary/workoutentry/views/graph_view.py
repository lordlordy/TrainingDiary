import os
import matplotlib
import datetime
# this is to prevent trying to show window with image.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from numpy.polynomial.polynomial import polyfit
from django.shortcuts import render
from django.conf import settings
from workoutentry.forms import GraphForm, PopularGraphsForm
from workoutentry.data_warehouse import DataWarehouse, Graph, ScatterGraph, POPULAR_GRAPHS

HEADINGS = DataWarehouse.TIME_SERIES_VARIABLES + Graph.GRAPH_VARIABLES
ARRAY_NAMES = [f'{h}_array' for h in HEADINGS]
HEADING_MAPPINGS = dict(zip(ARRAY_NAMES, HEADINGS))


def graph_view(request):

    if request.method == 'POST':
        graphs = []
        title = "All Dates"
        form_defaults = dict()

        print(request.POST)
        for key, value in request.POST.dict().items():
            print(f'{key}: {value}')


        if 'popular' in request.POST:
            title = request.POST['popular']

            popular_graph = POPULAR_GRAPHS[title]
            for i in range(popular_graph['number_of_plots']):
                g = []
                for a in ARRAY_NAMES:
                    print(a)
                    g.append((a, popular_graph[a][i]))
                graphs.append(g)
            display_type = popular_graph['graph_display_type']
            kwargs = {'colour_map': GraphForm.colour_map[int(popular_graph['colour_map'])],
                      'background': popular_graph['background'],
                      'from_date': popular_graph['from'],
                      'to_date': popular_graph['to']
                      }
            form_defaults = dict()
            for i in graphs[0]:
                form_defaults[i[0].replace('_array','')] = i[1]
            form_defaults['colour_map'] = popular_graph['colour_map']
            form_defaults['background'] = popular_graph['background']
            form_defaults['from'] = popular_graph['from']
            form_defaults['to'] = popular_graph['to']
            form_defaults['graph_display_type'] = display_type
            print(form_defaults)
        else:
            form_defaults = request.POST
            if ARRAY_NAMES[0] in request.POST:
                for i in range(0, len(request.POST.getlist(ARRAY_NAMES[0]))):
                    g = []
                    for a in ARRAY_NAMES:
                        g.append((a, request.POST.getlist(a)[i]))
                    graphs.append(g)

            if 'refresh' not in request.POST:
                new_graph = [request.POST.get(k) for k in HEADINGS]
                new = list(zip(ARRAY_NAMES, new_graph))
                graphs.append(new)

            display_type = request.POST['graph_display_type']

            kwargs = {'colour_map': GraphForm.colour_map[int(request.POST['colour_map'])],
                      'background': request.POST['background']}

            title_components = []

            if 'from' in request.POST:
                if len(request.POST['from']) > 0:
                    kwargs['from_date'] = request.POST['from']
                    title_components.append(f"From {request.POST['from']}")

            if 'to' in request.POST:
                if len(request.POST['to']) > 0:
                    kwargs['to_date'] = request.POST['to']
                    title_components.append(f"To {request.POST['to']}")

            if len(title_components) > 0:
                title = ' '.join(title_components)

        file_name = f'graph-{datetime.datetime.now().strftime("%Y:%m:%d:%H:%M:%S")}'

        time_series_graphs, scatter_graphs = create_graphs_for_plotting(graphs)

        if display_type == GraphForm.SINGLE or len(graphs) == 1:
            if len(time_series_graphs) == 0:
                if len(scatter_graphs) > 0:
                    save_scatter_image(scatter_graphs[0], file_name, **kwargs)
            else:
                save_image(time_series_graphs, file_name, **kwargs)
        else:
            if len(time_series_graphs) == 0 and len(scatter_graphs) == 1:
                save_scatter_image(scatter_graphs[0], file_name, **kwargs)
            else:
                save_multiplot_image(time_series_graphs, scatter_graphs, file_name, **kwargs)

        return render(request, 'workoutentry/graphs.html', {'selection_form': GraphForm(form_defaults),
                                                            'popular_form': PopularGraphsForm(),
                                                            'graph_headings': (DataWarehouse.TIME_SERIES_VARIABLES
                                                                               + Graph.GRAPH_VARIABLES),
                                                            'graphs': graphs,
                                                            'title': title,
                                                            'graph_img': f'tmp/{file_name}.png'})

    return render(request, 'workoutentry/graphs.html', {'selection_form': GraphForm(), 'popular_form': PopularGraphsForm()})


def save_scatter_image(scatter_graph, file_name, colour_map='rainbow', background='whitesmoke',
                       from_date=datetime.date(2000,1,1), to_date=datetime.date(2020,1,1)):

    fig = plt.figure(figsize=[24, 13.5])
    if scatter_graph.is_heatmap():
        add_heat_to(scatter_graph, fig, None, colour_map, background, from_date, to_date)
    else:
        add_scatter_to(scatter_graph, fig, None, colour_map, background, from_date, to_date)
    fig.savefig(os.path.join(settings.BASE_DIR, f'workoutentry/static/tmp/{file_name}'), bbox_inches='tight')
    plt.close(fig)


def add_heat_to(scatter_graph, fig, grid_spec=None, colour_map='rainbow', background='whitesmoke',
                       from_date=datetime.date(2000,1,1), to_date=datetime.date(2020,1,1)):

    x_series, y_series, name, x_name, y_name = scatter_graph.time_series()
    x = x_series.loc[from_date:to_date].values
    y = y_series.loc[from_date:to_date].values

    if grid_spec is None:
        gs = matplotlib.gridspec.GridSpec(3, 3)
    else:
        gs = matplotlib.gridspec.GridSpecFromSubplotSpec(3, 3, subplot_spec=grid_spec)

    axMain = plt.Subplot(fig, gs[:, :])
    axMain.set_facecolor(background)
    axMain.title.set_text(name)
    fig.add_subplot(axMain)

    h = axMain.hexbin(x, y, cmap=plt.get_cmap(colour_map), gridsize=scatter_graph.x.size())
    axMain.axis([x.min(), x.max(), y.min(), y.max()])
    axMain.grid(True, linestyle='-', alpha=0.5)

    cb = fig.colorbar(h)
    cb.set_label('observations')


def add_scatter_to(scatter_graph, fig, grid_spec=None, colour_map='rainbow', background='whitesmoke',
                       from_date=datetime.date(2000,1,1), to_date=datetime.date(2020,1,1)):


    x_series, y_series, name, x_name, y_name = scatter_graph.time_series()

    x = x_series.loc[from_date:to_date].values
    y = y_series.loc[from_date:to_date].values

    i = 0
    color_idx = np.linspace(0, 1, 4)
    c_map = plt.get_cmap(colour_map)

    if grid_spec is None:
        gs = matplotlib.gridspec.GridSpec(3, 3)
    else:
        gs = matplotlib.gridspec.GridSpecFromSubplotSpec(3,3, subplot_spec=grid_spec)

    axMain = plt.Subplot(fig, gs[:, :])
    if scatter_graph.include_histogram():
        axMain = plt.Subplot(fig, gs[1:, :2])
    axMain.set_facecolor(background)
    fig.add_subplot(axMain)
    axMain.scatter(x, y, color=c_map(color_idx[i]), s=scatter_graph.size())
    i += 1
    c, p1 = polyfit(x, y, 1)
    axMain.plot(x, c + p1 * x, color=c_map(color_idx[i]), dashes=[3,3])
    i += 1

    if scatter_graph.include_histogram():
        ax1 = plt.Subplot(fig, gs[0, :2], sharex=axMain)
        ax2 = plt.Subplot(fig, gs[1:, 2], sharey=axMain)
        fig.add_subplot(ax1)
        fig.add_subplot(ax2)

        ax1.set_facecolor(background)
        ax1.title.set_text(x_name)
        ax2.set_facecolor(background)
        ax2.title.set_text(y_name)


        min_x = np.nanmin(x)
        max_x = np.nanmax(x)
        x_width = (max_x - min_x) / 20
        min_y = np.nanmin(y)
        max_y = np.nanmax(y)
        y_width = (max_y - min_y) / 20
        # to avoid plotting loads of zeroes
        increment = 0
        if scatter_graph.x.is_day_not_rolling():
            increment = 0.01
        xbins = np.arange(min_x + increment, max_x + x_width, x_width)
        ybins = np.arange(min_y + increment, max_y + y_width, y_width)

        ax1.hist(x, bins=xbins, color=c_map(color_idx[i]))
        i += 1
        ax2.hist(y, bins=ybins, orientation='horizontal', color=c_map(color_idx[i]))
    else:
        axMain.title.set_text(name)

    fig.subplots_adjust(wspace=0, hspace=0)


def save_multiplot_image(graphs, scatter_graphs, file_name, colour_map='rainbow', background='whitesmoke',
                         from_date=datetime.date(2000,1,1), to_date=datetime.date(2020,1,1)):

    fig = plt.figure(figsize=[24, 13.5])
    rows, cols = multi_plot_dimensions(len(graphs) + len(scatter_graphs))
    gs = matplotlib.gridspec.GridSpec(rows, cols, wspace=0.2, hspace=0.2)

    i = 0
    color_idx = np.linspace(0, 1, len(graphs))
    c_map = plt.get_cmap(colour_map)

    for graph in graphs:
        time_series, name = graph.time_series()
        time_series = time_series.loc[from_date:to_date]
        ax = plt.Subplot(fig, gs[i])
        ax.grid()
        ax.set_facecolor(background)
        ax.title.set_text(name)
        if graph.is_bar():
            test = (max(time_series.index.values) - min(time_series.index.values)) / (24 * 60 * 60 * 1000000000)
            width = -float(test) / len(time_series.values)
            ax.bar(time_series.index.values, time_series.values, label=name, color=c_map(color_idx[i]),
                   align='edge', width=width, alpha=0.5)
        else:
            ax.plot(time_series, color=c_map(color_idx[i]), label=name, linewidth=graph.size(),
                    markersize=graph.size(), linestyle=graph.line_style(), marker=graph.marker())
            if graph.is_fill():
                ax.fill_between(time_series.index.values, 0, time_series.values, color=c_map(color_idx[i]), alpha=0.5)

        fig.add_subplot(ax)
        i += 1

    for graph in scatter_graphs:
        if graph.is_heatmap():
            add_heat_to(graph, fig, gs[i], colour_map, background, from_date, to_date)
        else:
            add_scatter_to(graph, fig, gs[i], colour_map, background, from_date, to_date)
        i += 1

    fig.savefig(os.path.join(settings.BASE_DIR, f'workoutentry/static/tmp/{file_name}'), bbox_inches='tight')
    plt.close(fig)


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
        time_series, name = graph.time_series()
        time_series = time_series.loc[from_date:to_date]
        ax = ax_primary
        if graph.is_secondary():
            ax = ax_secondary
        if graph.is_bar():
            test = (max(time_series.index.values) - min(time_series.index.values)) / (24 * 60 * 60 * 1000000000)
            width = -float(test) / len(time_series.values)
            ax.bar(time_series.index.values, time_series.values, label=name, color=c_map(color_idx[i]),
                   align='edge', width=width, alpha=0.5)
        else:
            ax.plot(time_series, color=c_map(color_idx[i]), label=name, linewidth=graph.size(),
                    markersize=graph.size(), linestyle=graph.line_style(), marker=graph.marker())
            if graph.is_fill():
                ax.fill_between(time_series.index.values, 0, time_series.values, color=c_map(color_idx[i]), alpha=0.5)

        i += 1

    ax_primary.set_facecolor(background)
    ax_primary.legend(loc=2)
    ax_secondary.legend(loc=1)
    fig.savefig(os.path.join(settings.BASE_DIR, f'workoutentry/static/tmp/{file_name}'), bbox_inches='tight')
    plt.close(fig)


def create_graphs_for_plotting(graphs):
    graphs_for_plotting = []
    scatter_graphs_for_plotting = []
    scatter_graphs = []
    for graph in graphs:
        g = create_graph_dict(graph)
        if g.is_scatter():
            scatter_graphs.append(g)
        else:
            graphs_for_plotting.append(g)

    pair = []
    for g in scatter_graphs:
        pair.append(g)
        if len(pair) == 2:
            scatter_graphs_for_plotting.append(ScatterGraph(pair[0], pair[1]))
            pair = []
    # nb a single scatter graph left over will not be plotted

    return graphs_for_plotting, scatter_graphs_for_plotting


def create_graph_dict(graph):
    d = dict()
    for k, v in graph:
        value = v
        if v == 'No':
            value = False
        if v == 'Yes':
            value = True
        try:
            value = int(v)
        except Exception:
            pass
        d[HEADING_MAPPINGS[k]] = value
    return Graph(**d)


def multi_plot_dimensions(n_of_graphs):
    rows = int(np.ceil(np.sqrt(n_of_graphs)))
    cols = rows - 1
    while cols * rows < n_of_graphs:
        cols += 1
    return rows, cols
