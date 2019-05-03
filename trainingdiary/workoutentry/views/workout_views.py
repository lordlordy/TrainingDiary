from django.views.generic import ListView, UpdateView, CreateView, DeleteView
from workoutentry.models import (Workout)


class WorkoutListView(ListView):
    model = Workout


class WorkoutUpdateView(UpdateView):
    model = Workout


class WorkoutCreateView(CreateView):
    model = Workout
    fields = ['date', 'activity']