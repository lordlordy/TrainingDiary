from django.shortcuts import render
from django.db.models import Sum, Count
from workoutentry.models import Workout
import datetime


def summary_view(request):
    ytd = dict()
    ytd['swim'] = Workout.objects.filter(day__date__year=datetime.datetime.now().year, activity='Swim').aggregate(
        km=Sum('km'), duration=Sum('duration')
    )
    ytd['bike'] = Workout.objects.filter(day__date__year=datetime.datetime.now().year, activity='Bike').aggregate(
        km=Sum('km'), duration=Sum('duration')
    )
    ytd['run'] = Workout.objects.filter(day__date__year=datetime.datetime.now().year, activity='Run').aggregate(
        km=Sum('km'), duration=Sum('duration')
    )
    print(ytd)
    return render(request, 'workoutentry/summary.html', {'ytd': ytd})
