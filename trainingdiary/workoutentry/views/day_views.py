from django.views.generic import UpdateView
import dateutil
from django.shortcuts import render
from django.http import HttpResponseRedirect
import datetime
from workoutentry.training_data import TrainingDataManager
from workoutentry.forms import DayFilterForm, DayEditForm
from workoutentry.models import Day


def days_list_view(request):
    month_ago = datetime.date.today() - datetime.timedelta(days=30)
    context = {'days': TrainingDataManager().days_between(from_date=month_ago, to_date=datetime.date.today()),
               'form': DayFilterForm()}

    if request.method == 'POST':
        if 'to' in request.POST and 'from' in request.POST:
            context['days'] = TrainingDataManager().days_between(from_date=request.POST['from'], to_date=request.POST['to'])
            context['form'] = DayFilterForm(initial={'from': request.POST['from'], 'to': request.POST['to']})

    return render(request, 'workoutentry/day_list.html', context)


class DayUpdateView(UpdateView):

    def get(self, request, *args, **kwargs):
        day = TrainingDataManager().days_between(kwargs['date'], kwargs['date'])
        print(day)
        return render(request, 'workoutentry/day_form.html', {'day': day[0], 'form': DayEditForm(initial=day[0].data_dictionary())})

    def post(self, request, *args, **kwargs):
        TrainingDataManager().update_day(kwargs['date'], request.POST['day_type'], request.POST['comments'])
        return HttpResponseRedirect(f'/trainingdiary/days/update/{kwargs["date"]}')


def new_day_view(request):
    if request.method == 'GET':
        tdm = TrainingDataManager()
        lastest_date = dateutil.parser.parse(tdm.latest_date()[0]).date()
        next_date = lastest_date + datetime.timedelta(days=1)
        day_args = [str(next_date), "Normal", ""]
        day = Day(*day_args)
        tdm.save_day(day.date_str, day.day_type, day.comments)
        form = DayEditForm(initial=day.data_dictionary())
        return render(request, 'workoutentry/day_form.html', {'day': day, 'form': form})
    if request.method == 'POST':

        tdm = TrainingDataManager()
        tdm.save_day(request.POST['date'], request.POST['day_type'], request.POST['comments'])
        return HttpResponseRedirect(f'/trainingdiary/days/')
