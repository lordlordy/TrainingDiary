from django.views.generic import UpdateView, CreateView, DeleteView
from django.forms.widgets import Select
from django import forms
from django.http import HttpResponseRedirect
from workoutentry.models import (Workout, Day, Reading)
from workoutentry.training_data import TrainingDataManager
from workoutentry.forms import WorkoutEditForm
import datetime
from django.shortcuts import render
import pandas as pd


def workouts_list_view(request):
    month_ago = datetime.date.today() - datetime.timedelta(days=30)
    context = {'workouts': TrainingDataManager().workouts_between(from_date=month_ago, to_date=datetime.date.today())}
    return render(request, 'workoutentry/workout_list.html', context)


class WorkoutUpdateView(UpdateView):

    def get(self, request, *args, **kwargs):
        workouts = TrainingDataManager().workout_for_date_and_number(kwargs["date"], kwargs["workout_number"])
        if len(workouts) > 0:
            return render(request, 'workoutentry/workout_form.html', {'workout': workouts[0],
                                                                      'form': WorkoutEditForm(initial=workouts[0].data_dictionary())})


    def post(self, request, *args, **kwargs):
        seconds = pd.to_timedelta(request.POST['seconds']).seconds
        TrainingDataManager().update_workout(kwargs['date'], kwargs['workout_number'], request.POST['activity'],
                                             request.POST['activity_type'], request.POST['equipment'],
                                             seconds, request.POST['rpe'], request.POST['tss'],
                                             request.POST['tss_method'], request.POST['km'], request.POST['kj'],
                                             request.POST['ascent_metres'], request.POST['reps'],
                                             request.POST['is_race'], request.POST['cadence'], request.POST['watts'],
                                             request.POST['watts_estimated'], request.POST['heart_rate'],
                                             request.POST['is_brick'], request.POST['keywords'],
                                             request.POST['comments'])
        return HttpResponseRedirect(f'/trainingdiary/workouts/{kwargs["date"]}/{kwargs["workout_number"]}')



class WorkoutCreateView(CreateView):
    model = Workout
    success_url = '/workouts/'
    fields = ['activity',
              'activity_type',
              'equipment',
              'duration',
              'rpe',
              'tss',
              'tss_method',
              'km',
              'kj',
              'ascent_metres',
              'reps',
              'is_race',
              'cadence',
              'watts',
              'watts_estimated',
              'heart_rate',
              'is_brick',
              'keywords',
              'comments']
    template_name = 'workoutentry/workout_form.html'

    def get_success_url(self):
        day_pk = self.object.day.id
        return f'/trainingdiary/days/{day_pk}'

    def form_valid(self, form):
        day = Day.objects.get(pk=self.kwargs['day_pk'])
        form.instance.day = day
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        unique_activities = Workout.objects.values('activity').distinct()
        unique_activities_types = Workout.objects.values('activity_type').distinct()
        unique_tss_methods = Workout.objects.values('tss_method').distinct()
        unique_equipment = Workout.objects.values('equipment').distinct()
        form.fields['activity'] = forms.CharField(required=False,
                                              widget=Select(choices=[(a['activity'], a['activity']) for a in unique_activities],
                                                            attrs={'class': 'form-control', 'id': 'activity'}))
        form.fields['activity_type'] = forms.CharField(required=False,
                                              widget=Select(choices=[(a['activity_type'], a['activity_type']) for a in unique_activities_types],
                                                            attrs={'class': 'form-control', 'id': 'activity_type'}))
        form.fields['tss_method'] = forms.CharField(required=False,
                                              widget=Select(choices=[(a['tss_method'], a['tss_method']) for a in unique_tss_methods],
                                                            attrs={'class': 'form-control', 'id': 'tss_method'}))
        form.fields['equipment'] = forms.CharField(required=False,
                                                    widget=Select(choices=[(a['equipment'], a['equipment']) for a in
                                                                           unique_equipment],
                                                                  attrs={'class': 'form-control', 'id': 'equipment'}))
        return form


class WorkoutDeleteView(DeleteView):
    model = Workout
    template_name = 'workoutentry/confirm_delete.html'

    def get_success_url(self):
        day_pk = self.object.day.id
        return f'/trainingdiary/days/{day_pk}'