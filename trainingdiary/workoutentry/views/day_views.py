from django.views.generic import UpdateView, CreateView
from workoutentry.models import Day
from django.shortcuts import render
from django.http import HttpResponseRedirect
import datetime
from workoutentry.training_data import TrainingDataManager
from workoutentry.forms import DayFilterForm, DayEditForm


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
        return render(request, 'workoutentry/day_form.html', {'day': day[0], 'form': DayEditForm(initial=day[0].data_dictionary())})


    def post(self, request, *args, **kwargs):
        TrainingDataManager().update_day(kwargs['date'], request.POST['day_type'], request.POST['comments'])
        return HttpResponseRedirect(f'/trainingdiary/days/{kwargs["date"]}')



class DayCreateView(CreateView):
    model = Day
    fields = ['date',
              'sleep',
              'sleep_quality',
              'fatigue',
              'motivation',
              'type',
              'comments']
    template_name = 'workoutentry/day_form.html'

    def get_success_url(self):
        day_pk = self.object.id
        return f'/trainingdiary/days/{day_pk}'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        from django.forms.widgets import TextInput
        form.fields['date'].widget = TextInput(attrs={'class': 'datepicker', 'placeholder': 'YYYY-MM-DD'})
        return form