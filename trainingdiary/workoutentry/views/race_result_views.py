from django.views.generic import UpdateView, DeleteView
from django.http import HttpResponseRedirect
from workoutentry.training_data import TrainingDataManager
from workoutentry.forms import RaceResultEditForm
from django.shortcuts import render
import pandas as pd


def race_results_list_view(request):
    context = {'race_results': TrainingDataManager().race_results()}
    return render(request, 'workoutentry/race_result_list.html', context)


class RaceResultUpdateView(UpdateView):

    def get(self, request, *args, **kwargs):
        race_results = TrainingDataManager().race_result_for_date_and_number(kwargs["date"], kwargs["race_number"])
        if len(race_results) > 0:
            return render(request, 'workoutentry/race_result_form.html', {'race_result': race_results[0],
                                                                      'form': RaceResultEditForm(initial=race_results[0].data_dictionary())})


    def post(self, request, *args, **kwargs):
        swim_seconds = pd.to_timedelta(request.POST['swim_seconds']).seconds
        t1_seconds = pd.to_timedelta(request.POST['t1_seconds']).seconds
        bike_seconds = pd.to_timedelta(request.POST['bike_seconds']).seconds
        t2_seconds = pd.to_timedelta(request.POST['t2_seconds']).seconds
        run_seconds = pd.to_timedelta(request.POST['run_seconds']).seconds
        print(request.POST)
        TrainingDataManager().update_race_result(kwargs['date'], kwargs['race_number'], request.POST['type'],
                                                 request.POST['brand'], request.POST['distance'], request.POST['name'],
                                                 request.POST['category'], request.POST['overall_position'],
                                                 request.POST['category_position'], swim_seconds, t1_seconds,
                                                 bike_seconds, t2_seconds, run_seconds, request.POST['swim_km'],
                                                 request.POST['bike_km'], request.POST['run_km'],
                                                 request.POST['comments'], request.POST['race_report'])

        return HttpResponseRedirect(f'/trainingdiary/race_results/{kwargs["date"]}/{kwargs["race_number"]}')


class RaceResultDeleteView(DeleteView):

    def get(self, request, *args, **kwargs):
        return render(request, 'workoutentry/confirm_delete.html',
                      {'object': f'Race result {kwargs["race_number"]} on {kwargs["date"]}'} )

    def post(self, request, *args, **kwargs):
        tdm = TrainingDataManager()
        tdm.delete_race_result(kwargs['date'], kwargs['race_number'])
        return render(request, 'workoutentry/race_result_list.html', {'race_results': tdm.race_results()})