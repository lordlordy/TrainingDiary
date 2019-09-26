from django.shortcuts import render
from workoutentry.training_data import TrainingDataManager
from workoutentry.data_warehouse import DataWarehouse
import datetime
import functools
import operator

TOTAL_TIME = 'Total Time'
TOTAL_KM = 'Total KM'
TOTAL_ASCENT = 'Ascent(m)'
SWIM_TIME = 'Swim Time'
SWIM_KM = 'Swim KM'
BIKE_TIME = 'Bike Time'
BIKE_KM = 'Bike KM'
RUN_TIME = 'Run Time'
RUN_KM = 'Run KM'

SUMMARY_HEADINGS = [TOTAL_TIME, TOTAL_KM, TOTAL_ASCENT, SWIM_TIME, SWIM_KM, BIKE_TIME, BIKE_KM, RUN_TIME, RUN_KM]

def summary_view(request):
    data = []

    tdm = TrainingDataManager()
    workouts = tdm.workouts()

    swim_km= functools.reduce(operator.add, [w.km for w in workouts if w.activity == 'Swim'])
    swim_seconds = functools.reduce(operator.add, [w.seconds for w in workouts if w.activity == 'Swim'])
    bike_km = functools.reduce(operator.add, [w.km for w in workouts if w.activity == 'Bike'])
    bike_seconds = functools.reduce(operator.add, [w.seconds for w in workouts if w.activity == 'Bike'])
    run_km = functools.reduce(operator.add, [w.km for w in workouts if w.activity == 'Run'])
    run_seconds = functools.reduce(operator.add, [w.seconds for w in workouts if w.activity == 'Run'])
    total_km = functools.reduce(operator.add, [w.km for w in workouts])
    total_seconds = functools.reduce(operator.add, [w.seconds for w in workouts])
    total_ascent = functools.reduce(operator.add, [w.ascent_metres for w in workouts])

    lifetime = ['Lifetime',
                total_seconds, int(total_km), total_ascent,
                swim_seconds, int(swim_km),
                bike_seconds, int(bike_km),
                run_seconds, int(run_km)
                ]

    data.append(lifetime)

    end = datetime.datetime.now().date()
    start = datetime.date(end.year, 1, 1)
    data.append(['YTD'] + values_for_range_list(start, end, workouts))

    end = datetime.date(end.year-1, end.month, end.day)
    start = datetime.date(end.year, 1, 1)
    data.append(['YTD Last Year'] + values_for_range_list(start, end, workouts))

    end = datetime.datetime.now().date()
    start = datetime.date(end.year-1, end.month, end.day-1)
    data.append(['R Year'] + values_for_range_list(start, end, workouts))

    end = datetime.date(end.year-1, end.month, end.day)
    start = datetime.date(end.year-1, end.month, end.day-1)
    data.append(['R Year Last Year'] + values_for_range_list(start, end, workouts))

    end = datetime.datetime.now().date()
    start = datetime.date(end.year, end.month, 1)
    data.append(['MTD'] + values_for_range_list(start, end, workouts))

    end = datetime.date(end.year-1, end.month, end.day)
    start = datetime.date(end.year, end.month, 1)
    data.append(['MTD Last Year'] + values_for_range_list(start, end, workouts))

    equipment_summary = DataWarehouse.instance().equipment_km_annual_summary()
    headings = [i for i in equipment_summary['All'].keys()]
    values = list()
    values.append(['Total'] + [int(equipment_summary['All'][h]) for h in headings])
    for k in equipment_summary:
        if k != 'All':
            values.append([k] + [int(equipment_summary[k][h]) for h in headings])

    activity_summary = DataWarehouse.instance().activity_summary()
    hours_values = list()
    km_values = list()
    hours_values.append(['Total'] + [int(activity_summary['All'][h][0]) for h in headings])
    km_values.append(['Total'] + [int(activity_summary['All'][h][1]) for h in headings])
    for k in activity_summary:
        if k != 'All':
            hours_values.append([k] + [int(activity_summary[k][h][0]) for h in headings])
            km_values.append([k] + [int(activity_summary[k][h][1]) for h in headings])

    headings = [""] + headings
    return render(request, 'workoutentry/summary.html', {'headings': SUMMARY_HEADINGS, 'data': data,
                                                         'summary_headings': headings,
                                                         'equipment_summary': values,
                                                         'hours_summary': hours_values,
                                                         'km_summary': km_values})


def values_for_range_list(start, end, workouts):
    swim = [w for w in workouts if w.activity == 'Swim' and w.date >= start and w.date <= end]
    bike = [w for w in workouts if w.activity == 'Bike' and w.date >= start and w.date <= end]
    run = [w for w in workouts if w.activity == 'Run' and w.date >= start and w.date <= end]
    total = [w for w in workouts if w.date >= start and w.date <= end]

    swim_km = swim_seconds = 0
    bike_km = bike_seconds = 0
    run_km = run_seconds = 0
    total_km = total_seconds = total_ascent = 0

    if len(swim) > 0:
        swim_km= functools.reduce(operator.add, [w.km for w in swim])
        swim_seconds = functools.reduce(operator.add, [w.seconds for w in swim])

    if len(bike) > 0:
        bike_km = functools.reduce(operator.add, [w.km for w in bike])
        bike_seconds = functools.reduce(operator.add, [w.seconds for w in bike])

    if len(run) > 0:
        run_km = functools.reduce(operator.add, [w.km for w in run])
        run_seconds = functools.reduce(operator.add, [w.seconds for w in run])

    if len(total) > 0:
        total_km = functools.reduce(operator.add, [w.km for w in total])
        total_seconds = functools.reduce(operator.add, [w.seconds for w in total])
        total_ascent = functools.reduce(operator.add, [w.ascent_metres for w in total])

    return [total_seconds, int(total_km), total_ascent, swim_seconds, int(swim_km), bike_seconds, int(bike_km), run_seconds, int(run_km)]
