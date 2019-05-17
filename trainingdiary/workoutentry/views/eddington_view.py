from django.shortcuts import render
from django.conf import settings
import os
from workoutentry.forms import EddingtonNumberForm
from workoutentry.data_warehouse import DataWarehouse
import matplotlib
# this is to prevent trying to show window with image.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd


def eddington_view(request):

    if request.method == 'POST':

        series = DataWarehouse.instance().time_series(request.POST['period'],
                                                      request.POST['activity'],
                                                      request.POST['activity_type'],
                                                      request.POST['equipment'],
                                                      request.POST['measure'])

        if series is None:
            return render(request, 'workoutentry/eddington_numbers.html', {'selection_form': EddingtonNumberForm()})

        unit = (request.POST['activity']
                + ':' + request.POST['period']
                + ':' + request.POST['activity_type']
                + ':' + request.POST['equipment']
                + ':' + request.POST['measure'])
        data = []
        ltd = []
        annual = []

        for date, value in series.iteritems():
            data.append((str(date), value))

        ed_num, ltd_hist, annual_hist, annual_summary = DataWarehouse.instance().eddington_history(series)

        save_image(ltd_hist, 'ltd.png')
        save_image(annual_hist, 'annual.png')

        for i in ltd_hist:
            ltd.append((str(i[0]), i[1], i[2], i[3]))
        for i in annual_hist:
            annual.append((str(i[0]), i[1], i[2], i[3]))


        return render(request, 'workoutentry/eddington_numbers.html',
                      {'selection_form': EddingtonNumberForm(),
                       'unit': unit,
                       'ed_num': ed_num,
                       'ltd': ltd,
                       'annual_ed_num': annual_summary[len(annual_summary)-1][1],
                       'annual': annual,
                       'annual_summary': annual_summary,
                       'ltd_img': f'/media/ltd.png',
                       'annual_img:': f'/media/annual.png'})

    return render(request, 'workoutentry/eddington_numbers.html', {'selection_form': EddingtonNumberForm()})


def save_image(data, file_name):
    df = pd.DataFrame(data, columns=['Date', 'Ed Num', 'Plus One', 'Contributor'])
    df['Date'] = pd.to_datetime(df['Date'])
    df['Plus One'] = df['Ed Num'] + df['Plus One']
    df.set_index(['Date'], inplace=True)

    fig = plt.figure(figsize=[24, 13.5])
    ax = fig.gca()
    ax.grid()
    ax.plot(df['Ed Num'], color='b', label='Ed Num', linewidth=3)
    ax.plot(df['Plus One'], color='y', label='Plus One')
    ax.plot(df['Contributor'], 'r.', label='Contributor')
    ax.legend()

    fig.savefig(os.path.join(settings.MEDIA_ROOT, file_name), bbox_inches='tight')
    plt.close(fig)
