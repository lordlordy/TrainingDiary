from django.views.generic import UpdateView
from django.http import HttpResponseRedirect
from workoutentry.training_data import TrainingDataManager
from workoutentry.forms import WorkoutEditForm, DayFilterForm
import datetime
from django.shortcuts import render
import pandas as pd


def workouts_list_view(request):
    month_ago = datetime.date.today() - datetime.timedelta(days=30)
    context = {'workouts': TrainingDataManager().workouts_between(from_date=month_ago, to_date=datetime.date.today()),
               'form': DayFilterForm()}

    if request.method == 'POST':
        if 'to' in request.POST and 'from' in request.POST:
            context['workouts'] = TrainingDataManager().workouts_between(from_date=request.POST['from'], to_date=request.POST['to'])
            context['form'] = DayFilterForm(initial={'from': request.POST['from'], 'to': request.POST['to']})

    return render(request, 'workoutentry/workout_list.html', context)


class WorkoutUpdateView(UpdateView):

    def get(self, request, *args, **kwargs):
        workouts = TrainingDataManager().workout_for_date_and_number(kwargs["date"], kwargs["workout_number"])
        dd = workouts[0].data_dictionary()
        dd['watts_estimated_yes_no'] = 'Yes' if dd['watts_estimated'] > 0 else 'No'
        dd['is_race_yes_no'] = 'Yes' if dd['is_race'] > 0 else 'No'
        dd['is_brick_yes_no'] = 'Yes' if dd['is_brick'] > 0 else 'No'
        if len(workouts) > 0:
            return render(request, 'workoutentry/workout_form.html', {'workout': workouts[0],
                                                                      'form': WorkoutEditForm(initial=dd)})

    def post(self, request, *args, **kwargs):
        seconds = pd.to_timedelta(request.POST['seconds']).seconds
        watts_estimated = 1 if request.POST['watts_estimated_yes_no'] == 'Yes' else 0
        is_race = 1 if request.POST['is_race_yes_no'] == 'Yes' else 0
        is_brick = 1 if request.POST['is_brick_yes_no'] == 'Yes' else 0
        TrainingDataManager().update_workout(kwargs['date'], kwargs['workout_number'], request.POST['activity'],
                                             request.POST['activity_type'], request.POST['equipment'],
                                             seconds, request.POST['rpe'], request.POST['tss'],
                                             request.POST['tss_method'], request.POST['km'], request.POST['kj'],
                                             request.POST['ascent_metres'], request.POST['reps'], is_race,
                                             request.POST['cadence'], request.POST['watts'], watts_estimated,
                                             request.POST['heart_rate'], is_brick, request.POST['keywords'],
                                             request.POST['comments'])

        return HttpResponseRedirect(f'/trainingdiary/days/update/{kwargs["date"]}')


def new_workout_view(request, **kwargs):
    if request.method == 'GET':
        workout = TrainingDataManager().day_for_date(kwargs['date']).default_workout()
        dd = workout.data_dictionary()
        dd['watts_estimated_yes_no'] = 'Yes' if dd['watts_estimated'] > 0 else 'No'
        dd['is_race_yes_no'] = 'Yes' if dd['is_race'] > 0 else 'No'
        dd['is_brick_yes_no'] = 'Yes' if dd['is_brick'] > 0 else 'No'
        form = WorkoutEditForm(initial=dd)
        return render(request, 'workoutentry/workout_form.html', {'workout': workout,
                                                                      'form': form})

    if request.method == 'POST':
        seconds = pd.to_timedelta(request.POST['seconds']).seconds
        watts_estimated = 1 if request.POST['watts_estimated_yes_no'] == 'Yes' else 0
        is_race = 1 if request.POST['is_race_yes_no'] == 'Yes' else 0
        is_brick = 1 if request.POST['is_brick_yes_no'] == 'Yes' else 0
        TrainingDataManager().save_workout(kwargs['date'], request.POST['activity'], request.POST['activity_type'],
                                           request.POST['equipment'], seconds, request.POST['rpe'], request.POST['tss'],
                                           request.POST['tss_method'], request.POST['km'], request.POST['kj'],
                                           request.POST['ascent_metres'], request.POST['reps'], is_race,
                                           request.POST['cadence'], request.POST['watts'], watts_estimated,
                                           request.POST['heart_rate'], is_brick,request.POST['keywords'],
                                           request.POST['comments'])

        return HttpResponseRedirect(f'/trainingdiary/days/update/{kwargs["date"]}')


def delete_workout_view(request, **kwargs):
    if request.method == "GET":
        return render(request, 'workoutentry/confirm_delete.html',
                      {'object': f"workout {kwargs['workout_number']} on {kwargs['date']}"})
    if request.method == "POST":
        TrainingDataManager().delete_workout(kwargs['date'], kwargs['workout_number'])
        return HttpResponseRedirect(f'/trainingdiary/days/update/{kwargs["date"]}')
