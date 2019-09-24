from django.shortcuts import render
from workoutentry.training_data import TrainingDataManager
# from workoutentry.models import RaceResult
# import datetime
#
#
def home_view(request):
    results = sorted(TrainingDataManager().future_races(), key=lambda x: x.date)
    return render(request, 'mainsite/home.html', {'upcoming_races': results})


def ironman_results_view(request):
    results = sorted(TrainingDataManager().race_results_of_distance('Ironman'), key=lambda x: x.date, reverse=True)
    return render(request, 'mainsite/ironman_results.html', {'race_results': results})


def swimrun_results_view(request):
    results = sorted(TrainingDataManager().race_results_of_type('SwimRun'), key=lambda x: x.date, reverse=True)
    return render(request, 'mainsite/swimrun_results.html', {'race_results': results})


def all_results_view(request):
    print("getting race results")
    results = TrainingDataManager().race_results()
    print(results)
    return render(request, 'mainsite/all_results.html', {'race_results': results})


def race_results_view(request):

    results = sorted(TrainingDataManager().race_results(), key=lambda x: x.date, reverse=True)
    results_by_year = dict()
    for r in results:
        if r.year in results_by_year:
            results_by_year[r.year].append(r)
        else:
            results_by_year[r.year] = [r,]
    return render(request, 'mainsite/race_results.html', {'race_results': results_by_year})