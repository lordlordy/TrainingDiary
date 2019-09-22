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
        tdm = TrainingDataManager()
        readings = tdm.reading_for_date_and_type(kwargs['date'], kwargs['type'])
        if len(readings) > 0:
            form = ReadingEditForm(initial=readings[0].data_dictionary())
            r_types = tdm.reading_types_unused_for_date(kwargs['date'])
            r_types.append(readings[0].reading_type)
            form.fields['reading_type'].widget.choices = [(t,t) for t in r_types]
            return render(request, 'workoutentry/reading_form.html', {'reading': readings[0], 'form': form})


    def post(self, request, *args, **kwargs):
        TrainingDataManager().update_reading(kwargs['date'], request.POST['reading_type'], request.POST['value'])
        return HttpResponseRedirect(f'/trainingdiary/days/update/{kwargs["date"]}')


def new_reading_view(request, **kwargs):
    if request.method == 'GET':
        reading_args = [kwargs['date'], 'sleep', 8.0]
        reading = Reading(*reading_args)
        form = ReadingEditForm(initial=reading.data_dictionary())
        form.fields['reading_type'].widget.choices = [(t, t) for t in TrainingDataManager().reading_types_unused_for_date(kwargs['date'])]
        return render(request, 'workoutentry/reading_form.html', {'reading': reading,
                                                                  'form': form})
    if request.method == 'POST':
        tdm = TrainingDataManager()
        tdm.save_reading(kwargs['date'], request.POST['reading_type'], request.POST['value'])
        return HttpResponseRedirect(f'/trainingdiary/days/update/{kwargs["date"]}')


def delete_reading_view(request, **kwargs):
    if request.method == "GET":
        return render(request, 'workoutentry/confirm_delete.html',
                      {'object': f'Reading {kwargs["type"]} on {kwargs["date"]}'})
    if request.method == "POST":
        TrainingDataManager().delete_reading(kwargs['date'], kwargs['type'])
        return HttpResponseRedirect(f'/trainingdiary/days/update/{kwargs["date"]}')


