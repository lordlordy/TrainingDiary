from django.views.generic import UpdateView, DeleteView
from django.http import HttpResponseRedirect
from workoutentry.training_data import TrainingDataManager
from workoutentry.forms import RaceResultEditForm
from django.shortcuts import render
import pandas as pd
import dateutil
import datetime


def race_results_list_view(request):
    context = {'race_results': TrainingDataManager().race_results()}
    return render(request, 'workoutentry/race_result_list.html', context)


class RaceResultUpdateView(UpdateView):

    def get(self, request, *args, **kwargs):
        race_result = TrainingDataManager().race_result_for_date_and_number(kwargs["date"], kwargs["race_number"])
        if race_result is not None:
            form = RaceResultEditForm(initial=race_result.data_dictionary())
            form.fields['date'].widget.attrs['readonly'] = 'readonly'
            return render(request, 'workoutentry/race_result_form.html',
                          {'race_result': race_result, 'form': form})


    def post(self, request, *args, **kwargs):
        swim_seconds = pd.to_timedelta(request.POST['swim_seconds']).seconds
        t1_seconds = pd.to_timedelta(request.POST['t1_seconds']).seconds
        bike_seconds = pd.to_timedelta(request.POST['bike_seconds']).seconds
        t2_seconds = pd.to_timedelta(request.POST['t2_seconds']).seconds
        run_seconds = pd.to_timedelta(request.POST['run_seconds']).seconds
        TrainingDataManager().update_race_result(kwargs['date'], kwargs['race_number'], request.POST['type'],
                                                 request.POST['brand'], request.POST['distance'], request.POST['name'],
                                                 request.POST['category'], request.POST['overall_position'],
                                                 request.POST['category_position'], swim_seconds, t1_seconds,
                                                 bike_seconds, t2_seconds, run_seconds, request.POST['swim_km'],
                                                 request.POST['bike_km'], request.POST['run_km'],
                                                 request.POST['comments'], request.POST['race_report'])

        # return HttpResponseRedirect(f'/trainingdiary/race_results/{kwargs["date"]}/{kwargs["race_number"]}')
        return HttpResponseRedirect(f'/trainingdiary/race_results/')


class RaceResultDeleteView(DeleteView):

    def get(self, request, *args, **kwargs):
        return render(request, 'workoutentry/confirm_delete.html',
                      {'object': f'Race result {kwargs["race_number"]} on {kwargs["date"]}'} )

    def post(self, request, *args, **kwargs):
        tdm = TrainingDataManager()
        tdm.delete_race_result(kwargs['date'], kwargs['race_number'])
        return render(request, 'workoutentry/race_result_list.html', {'race_results': tdm.race_results()})


def new_race_result_view(request):
    if request.method == 'GET':
        default_dd = {'date': str(datetime.date.today()),
                      'type': 'SwimRUn',
                      'brand': 'OtillO',
                      'distance': 'Sprint',
                      'name': 'Descriptive Name',
                      'category': 'Mixed',
                      'overall_position': 0,
                      'category_position': 0,
                      'swim_seconds': 0,
                      't1_seconds': 0,
                      'bike_seconds': 0,
                      't2_seconds': 0,
                      'run_seconds': 0,
                      'swim_km': 0.0,
                      'bike_km': 0.0,
                      'run_km': 0.0}
        return render(request, 'workoutentry/race_result_form.html',
                      {'form': RaceResultEditForm(initial=default_dd)})

    if request.method == 'POST':
        print(request.POST)
        swim_seconds = 0 if request.POST['swim_seconds'] == '' else pd.to_timedelta(request.POST['swim_seconds']).seconds
        t1_seconds = 0 if request.POST['t1_seconds'] == '' else pd.to_timedelta(request.POST['t1_seconds']).seconds
        bike_seconds = 0 if request.POST['bike_seconds'] == '' else pd.to_timedelta(request.POST['bike_seconds']).seconds
        t2_seconds = 0 if request.POST['t2_seconds'] == '' else pd.to_timedelta(request.POST['t2_seconds']).seconds
        run_seconds = 0 if request.POST['run_seconds'] == '' else pd.to_timedelta(request.POST['run_seconds']).seconds
        swim_km = 0 if request.POST['swim_km'] == '' else request.POST['swim_km']
        bike_km = 0 if request.POST['bike_km'] == '' else request.POST['bike_km']
        run_km = 0 if request.POST['run_km'] == '' else request.POST['run_km']
        overall_position = 0 if request.POST['overall_position'] == '' else request.POST['overall_position']
        category_position = 0 if request.POST['category_position'] == '' else request.POST['category_position']
        tdm = TrainingDataManager()
        # NB - no race number is passed. The persistence layer establishes this for new race results
        tdm.save_race_result(request.POST['date'], None, request.POST['type'], request.POST['brand'],
                             request.POST['distance'], request.POST['name'], request.POST['category'], overall_position,
                             category_position, swim_seconds, t1_seconds, bike_seconds, t2_seconds, run_seconds,
                             swim_km, bike_km, run_km, request.POST['comments'], request.POST['race_report'])
        return HttpResponseRedirect(f'/trainingdiary/race_results/')
