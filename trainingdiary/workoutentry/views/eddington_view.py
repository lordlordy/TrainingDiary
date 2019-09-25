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
import datetime


def eddington_view(request):
    return _eddington_view(request, 'workoutentry/eddington_numbers.html')


def popular_eddington_view(request):
    return _eddington_view(request, 'workoutentry/eddington_numbers_simple.html')


def _eddington_view(request, template):
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
            else:
                df = pd.read_excel(uploaded_file)
            series = pd.Series(data=list(df.iloc[0:, 1]), index=df.iloc[0:,0])
            data = default_data
            #  added 'now' on to ensure cached image isn't used
            unit = f'{df.columns[1]}-{datetime.datetime.now().strftime("%Y:%m:%d:%H:%M:%S")}'
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
            return render(request, template, {'selection_form': EddingtonNumberForm(),
                                              'popular_form': PopularEddingtonNumberForm()})

        ed_num, ltd_hist, annual_hist, annual_summary, monthly_hist, monthly_summary = DataWarehouse.instance().eddington_history(series)

        ltd_image_name = f'ltd-{unit}'
        annual_image_name = f'annual-{unit}'
        monthly_image_name = f'monthly-{unit}'
        save_image(ltd_hist, ltd_image_name, unit)
        save_image(annual_hist, annual_image_name, unit)
        save_image(monthly_hist, monthly_image_name, unit)

        best_annual = max([v[1] for v in annual_hist])
        best_monthly = max([v[1] for v in monthly_hist])

        return render(request, template,
                      {'selection_form': EddingtonNumberForm(data),
                       'popular_form': PopularEddingtonNumberForm(),
                       'unit': unit,
                       'ed_num': ed_num,
                       'ltd': ltd_hist,
                       'annual_ed_num': annual_summary[len(annual_summary)-1][1],
                       'best_annual': best_annual,
                       'annual': annual_hist,
                       'annual_summary': annual_summary,
                       'monthly_ed_num': monthly_summary[len(monthly_summary)-1][1],
                       'best_monthly': best_monthly,
                       'monthly': monthly_hist,
                       'monthly_summary': monthly_summary,
                       'ltd_img': f'tmp/{ltd_image_name}.png',
                       'annual_img': f'tmp/{annual_image_name}.png',
                       'monthly_img': f'tmp/{monthly_image_name}.png'})

    return render(request, template, {'selection_form': EddingtonNumberForm(),
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

    fig.savefig(os.path.join(settings.BASE_DIR, f'workoutentry/static/tmp/{file_name}'), bbox_inches='tight')

    plt.close(fig)
