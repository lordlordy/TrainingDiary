from django.shortcuts import render
from django.conf import settings
import os
from workoutentry.forms import EddingtonNumberForm, PopularEddingtonNumberForm
from workoutentry.data_warehouse import DataWarehouse
import matplotlib
# this is to prevent trying to show window with image.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd


def eddington_view(request):
    default_data = {'period': "Day",
                    'aggregation': 'Sum',
                    'activity': 'All',
                    'activity_type': 'All',
                    'equipment': 'All',
                    'measure': 'km',
                    'to_date': 'No',
                    'rolling': 'No',
                    'rolling_periods': '1',
                    'rolling_aggregation': 'Sum',
                    'day_of_week': 'All',
                    'month': 'All',
                    'day_type': 'All',
                    }

    if request.method == 'POST':
        data = request.POST.dict()

        if 'document' in request.FILES:
            uploaded_file = request.FILES['document']
            #  todo there must be a better way to check this
            if uploaded_file.name[-3:] == 'csv':
                df = pd.read_csv(uploaded_file)
                df['Date'] = pd.to_datetime(df['Date'])
                df.dropna(inplace=True)
                print(df)
            else:
                df = pd.read_excel(uploaded_file)
                print(df)
            series = pd.Series(data=list(df.iloc[0:, 1]), index=df.iloc[0:,0])
            data = default_data
            unit = df.columns[1]
        else:
            if 'popular' in request.POST:
                data = default_data

                popular_data = DataWarehouse.popular_numbers[request.POST['popular']]
                data = {**data, **popular_data}

            series, unit = DataWarehouse.instance().time_series(period=data['period'],
                                                                aggregation=data['aggregation'],
                                                                activity=data['activity'],
                                                                activity_type=data['activity_type'],
                                                                equipment=data['equipment'],
                                                                measure=data['measure'],
                                                                to_date=data['to_date'] == 'Yes',
                                                                rolling=data['rolling'] == 'Yes',
                                                                rolling_periods=int(data['rolling_periods']),
                                                                rolling_aggregation=data['rolling_aggregation'],
                                                                day_of_week=data['day_of_week'],
                                                                month=data['month'],
                                                                day_type=data['day_type'])

        if series is None:
            return render(request, 'workoutentry/eddington_numbers.html', {'selection_form': EddingtonNumberForm(),
                                                                           'popular_form': PopularEddingtonNumberForm()})

        ltd = []
        annual = []

        ed_num, ltd_hist, annual_hist, annual_summary = DataWarehouse.instance().eddington_history(series)

        save_image(ltd_hist, 'ltd.png', unit)
        save_image(annual_hist, 'annual.png', unit)

        for i in ltd_hist:
            ltd.append((str(i[0]), i[1], i[2], i[3]))
        for i in annual_hist:
            annual.append((str(i[0]), i[1], i[2], i[3]))

        return render(request, 'workoutentry/eddington_numbers.html',
                      {'selection_form': EddingtonNumberForm(data),
                       'popular_form': PopularEddingtonNumberForm(),
                       'unit': unit,
                       'ed_num': ed_num,
                       'ltd': ltd,
                       'annual_ed_num': annual_summary[len(annual_summary)-1][1],
                       'annual': annual,
                       'annual_summary': annual_summary,
                       'ltd_img': f'/media/ltd.png',
                       'annual_img:': f'/media/annual.png'})

    return render(request, 'workoutentry/eddington_numbers.html', {'selection_form': EddingtonNumberForm(),
                                                                   'popular_form': PopularEddingtonNumberForm()})


def save_image(data, file_name, name):
    df = pd.DataFrame(data, columns=['Date', 'Ed Num', 'Plus One', 'Contributor'])
    df['Date'] = pd.to_datetime(df['Date'])
    df['Plus One'] = df['Ed Num'] + df['Plus One']
    df.set_index(['Date'], inplace=True)

    fig = plt.figure(figsize=[24, 13.5])
    ax = fig.gca()
    ax.set_title(name, fontsize=12)
    ax.grid()
    ax.plot(df['Ed Num'], color='b', label='Ed Num', linewidth=3)
    ax.plot(df['Plus One'], color='y', label='Plus One')
    ax.plot(df['Contributor'], 'r.', label='Contributor')
    ax.legend()

    fig.savefig(os.path.join(settings.MEDIA_ROOT, file_name), bbox_inches='tight')
    plt.close(fig)
