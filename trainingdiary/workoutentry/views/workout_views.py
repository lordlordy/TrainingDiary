from django.views.generic import ListView, UpdateView, CreateView
from django.forms.widgets import Select
from django import forms
from django.contrib.auth.decorators import login_required

from workoutentry.models import (Workout, Day)
from workoutentry.filters import WorkoutFilter

import datetime
from django.shortcuts import render


@login_required
def workouts_list_view(request):
    context = dict()
    if request.method == 'POST':
        df = WorkoutFilter(request.POST, Workout.objects.all())
        context['filter'] = df
        context['workouts'] = df.qs
    if request.method == 'GET':
        context['workouts'] = filtered_set()
        context['filter'] = WorkoutFilter()
    return render(request, 'workoutentry/workout_list.html', context)


def filtered_set():
    month_ago = datetime.date.today() - datetime.timedelta(days=30)
    return Workout.objects.filter(day__date__gt=month_ago)


class WorkoutListView(ListView):
    model = Workout
    context_object_name = 'workouts'

    def get_queryset(self):
        month_ago = datetime.date.today() - datetime.timedelta(days=30)
        return Workout.objects.filter(day__date__gt=month_ago)


class WorkoutUpdateView(UpdateView):
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

    def get_success_url(self):
        day_pk = self.object.day.id
        return f'/days/{day_pk}'

    def post(self, request, *args, **kwargs):
        post_reponse = super().post(request, args, kwargs)
        needs_saving = False
        if len(request.POST['new_activity']) > 0:
            self.object.activity = request.POST['new_activity']
            needs_saving = True

        if len(request.POST['new_activity_type']) > 0:
            self.object.activity_type = request.POST['new_activity_type']
            needs_saving = True

        if len(request.POST['new_equipment']) > 0:
            self.object.equipment = request.POST['new_equipment']
            needs_saving = True

        if len(request.POST['new_tss_method']) > 0:
            self.object.tss_method = request.POST['new_tss_method']
            needs_saving = True

        if needs_saving:
            self.object.save()

        print(f'new equipment: {request.POST["new_equipment"]}')
        return post_reponse

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        unique_activities = Workout.objects.values('activity').distinct()
        unique_activities_types = Workout.objects.values('activity_type').distinct()
        unique_tss_methods = Workout.objects.values('tss_method').distinct()
        unique_equipment = Workout.objects.values('equipment').distinct()
        form.fields['activity'] = forms.CharField(required=True,
                                              widget=Select(choices=[(a['activity'], a['activity']) for a in unique_activities],
                                                            attrs={'class': 'form-control', 'id': 'activity'}))
        form.fields['activity_type'] = forms.CharField(required=True,
                                              widget=Select(choices=[(a['activity_type'], a['activity_type']) for a in unique_activities_types],
                                                            attrs={'class': 'form-control', 'id': 'activity_type'}))
        form.fields['tss_method'] = forms.CharField(required=True,
                                              widget=Select(choices=[(a['tss_method'], a['tss_method']) for a in unique_tss_methods],
                                                            attrs={'class': 'form-control', 'id': 'tss_method'}))
        form.fields['equipment'] = forms.CharField(required=True,
                                                    widget=Select(choices=[(a['equipment'], a['equipment']) for a in
                                                                           unique_equipment],
                                                                  attrs={'class': 'form-control', 'id': 'equipment'}))
        return form

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
        return f'/days/{day_pk}'

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
        form.fields['activity'] = forms.CharField(required=True,
                                              widget=Select(choices=[(a['activity'], a['activity']) for a in unique_activities],
                                                            attrs={'class': 'form-control', 'id': 'activity'}))
        form.fields['activity_type'] = forms.CharField(required=True,
                                              widget=Select(choices=[(a['activity_type'], a['activity_type']) for a in unique_activities_types],
                                                            attrs={'class': 'form-control', 'id': 'activity_type'}))
        form.fields['tss_method'] = forms.CharField(required=True,
                                              widget=Select(choices=[(a['tss_method'], a['tss_method']) for a in unique_tss_methods],
                                                            attrs={'class': 'form-control', 'id': 'tss_method'}))
        form.fields['equipment'] = forms.CharField(required=True,
                                                    widget=Select(choices=[(a['equipment'], a['equipment']) for a in
                                                                           unique_equipment],
                                                                  attrs={'class': 'form-control', 'id': 'equipment'}))
        return form
