from django.shortcuts import render
from django.db.models import Sum
from workoutentry.models import Workout
import datetime

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

    swim = Workout.objects.filter(activity='Swim').aggregate(km=Sum('km'), time=Sum('duration'))
    bike = Workout.objects.filter(activity='Bike').aggregate(km=Sum('km'), time=Sum('duration'))
    run = Workout.objects.filter(activity='Run').aggregate(km=Sum('km'), time=Sum('duration'))
    total = Workout.objects.filter().aggregate(km=Sum('km'), time=Sum('duration'), ascent=Sum('ascent_metres'))

    lifetime = ['Lifetime',
                total['time'],total['km'], total['ascent'],
                swim['time'], swim['km'],
                bike['time'], bike['km'],
                run['time'], run['km']
                ]

    data.append(lifetime)

    end = datetime.datetime.now().date()
    start = datetime.date(end.year, 1, 1)
    data.append(['YTD'] + values_for_range_list(start, end))

    end = datetime.date(end.year-1, end.month, end.day)
    start = datetime.date(end.year, 1, 1)
    data.append(['YTD Last Year'] + values_for_range_list(start, end))

    end = datetime.datetime.now().date()
    start = datetime.date(end.year-1, end.month, end.day-1)
    data.append(['R Year'] + values_for_range_list(start, end))

    end = datetime.date(end.year-1, end.month, end.day)
    start = datetime.date(end.year-1, end.month, end.day-1)
    data.append(['R Year Last Year'] + values_for_range_list(start, end))

    end = datetime.datetime.now().date()
    start = datetime.date(end.year, end.month, 1)
    data.append(['MTD'] + values_for_range_list(start, end))

    end = datetime.date(end.year-1, end.month, end.day)
    start = datetime.date(end.year, end.month, 1)
    data.append(['MTD Last Year'] + values_for_range_list(start, end))

    return render(request, 'workoutentry/summary.html', {'headings': SUMMARY_HEADINGS, 'data': data})


def values_for_range_list(start, end):
    swim = Workout.objects.filter(day__date__gte=start, day__date__lte=end, activity='Swim').aggregate(km=Sum('km'), time=Sum('duration'))
    bike = Workout.objects.filter(day__date__gte=start, day__date__lte=end, activity='Bike').aggregate(km=Sum('km'),
                                                                                                       time=Sum('duration'))
    run = Workout.objects.filter(day__date__gte=start, day__date__lte=end, activity='Run').aggregate(km=Sum('km'), time=Sum('duration'))
    total = Workout.objects.filter(day__date__gte=start, day__date__lte=end).aggregate(km=Sum('km'), time=Sum('duration'),
                                                                                                       ascent=Sum('ascent_metres'))

    ytd = [total['time'], total['km'], total['ascent'],
           swim['time'], swim['km'],
           bike['time'], bike['km'],
           run['time'], run['km']
           ]

    return ytd