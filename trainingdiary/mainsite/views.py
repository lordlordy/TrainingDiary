from django.shortcuts import render
from workoutentry.models import RaceResult
import datetime


def home_view(request):
    upcoming_races = RaceResult.objects.filter(date__gte=datetime.datetime.now().date())
    return render(request, 'mainsite/home.html', {'upcoming_races': upcoming_races})


def ironman_results_view(request):
    ironman_results = RaceResult.objects.filter(distance='Ironman').order_by('-date')
    return render(request, 'mainsite/ironman_results.html', {'race_results': ironman_results})


def swimrun_results_view(request):
    swimrun_results = RaceResult.objects.filter(type='SwimRun').order_by('-date')
    return render(request, 'mainsite/swimrun_results.html', {'race_results': swimrun_results})


def all_results_view(request):
    results = RaceResult.objects.filter(date__lt=datetime.datetime.now().date()).order_by('-date')
    return render(request, 'mainsite/all_results.html', {'race_results': results})


def race_results_view(request):

    date_list = RaceResult.objects.all().dates('date', 'year').order_by('-date')
    results_by_year = dict()
    for year in date_list:
        results_by_year[year] = RaceResult.objects.filter(date__year=year.year, date__lt=datetime.datetime.now().date()).order_by('-date')
    return render(request, 'mainsite/race_results.html', {'race_results': results_by_year})