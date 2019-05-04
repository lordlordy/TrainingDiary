from django.views.generic import ListView, UpdateView, CreateView, DeleteView
from workoutentry.models import (Workout)


class WorkoutListView(ListView):
    model = Workout
    context_object_name = 'workouts'


class WorkoutUpdateView(UpdateView):
    model = Workout
    success_url = '/workouts/workouts/'
    fields = ['date',
              'activity',
              'activity_type',
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


class WorkoutCreateView(CreateView):
    model = Workout
    success_url = '/workouts/workouts/'
    fields = ['date',
              'activity',
              'activity_type',
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

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        from django.forms.widgets import TextInput
        form.fields['date'].widget = TextInput(attrs={'class': 'datepicker', 'placeholder': 'YYYY-MM-DD'})
        return form