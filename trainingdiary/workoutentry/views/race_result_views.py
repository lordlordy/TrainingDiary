from django.views.generic import UpdateView
from django.http import HttpResponseRedirect
from workoutentry.training_data import TrainingDataManager
from workoutentry.forms import WorkoutEditForm
from django.shortcuts import render
import pandas as pd


def race_results_list_view(request):
    context = {'race_results': TrainingDataManager().race_results()}
    return render(request, 'workoutentry/race_result_list.html', context)


class RaceResultUpdateView(UpdateView):

    def get(self, request, *args, **kwargs):
        workouts = TrainingDataManager().workout_for_date_and_number(kwargs["date"], kwargs["workout_number"])
        if len(workouts) > 0:
            return render(request, 'workoutentry/workout_form.html', {'workout': workouts[0],
                                                                      'form': WorkoutEditForm(initial=workouts[0].data_dictionary())})


    def post(self, request, *args, **kwargs):
        swim_seconds = pd.to_timedelta(request.POST['seconds']).seconds
        t1_seconds = pd.to_timedelta(request.POST['seconds']).seconds
        bike_seconds = pd.to_timedelta(request.POST['seconds']).seconds
        t2_seconds = pd.to_timedelta(request.POST['seconds']).seconds
        run_seconds = pd.to_timedelta(request.POST['seconds']).seconds
        TrainingDataManager().update_race_result(kwargs['date'], kwargs['race_number'], request.POST['type'],
                                                 request.POST['brand'], request.POST['distance'], request.POST['name'],
                                                 request.POST['category'], request.POST['overall_position'],
                                                 request.POST['category_position'], swim_seconds, t1_seconds,
                                                 bike_seconds, t2_seconds, run_seconds, request.POST['swim_km'],
                                                 request.POST['bike_km'], request.POST['run_km'],
                                                 request.POST['comments'], request.POST['race_report'])

        return HttpResponseRedirect(f'/trainingdiary/race_results/{kwargs["date"]}/{kwargs["race_number"]}')

