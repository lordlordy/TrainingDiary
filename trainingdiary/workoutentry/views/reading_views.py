from django.views.generic import UpdateView
from workoutentry.models import Reading
from django.shortcuts import render
from workoutentry.training_data import TrainingDataManager
from workoutentry.forms import DayFilterForm, DayEditForm, ReadingEditForm
from django.http import HttpResponseRedirect


class ReadingUpdateView(UpdateView):
    model = Reading
    success_url = '/days/'


    def get(self, request, *args, **kwargs):
        readings = TrainingDataManager().reading_for_date_and_type(kwargs['date'], kwargs['type'])
        if len(readings) > 0:
            return render(request, 'workoutentry/reading_form.html', {'reading': readings[0], 'form': ReadingEditForm()})


    def post(self, request, *args, **kwargs):
        TrainingDataManager().update_reading(kwargs['date'], request.POST['reading_type'], request.POST['value'])
        return HttpResponseRedirect(f'/trainingdiary/days/{kwargs["date"]}')





