from django.views.generic import ListView, UpdateView, CreateView
from workoutentry.models import (Day, KG, FatPercentage, RestingHeartRate, SDNN, RMSSD)
from workoutentry.filters import DayFilter
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django import forms
from django.forms.widgets import Select
import datetime


def days_list_view(request):
    context = dict()
    if request.method == 'POST':
        df = DayFilter(request.POST, Day.objects.all())
        context['filter'] = df
        context['days'] = df.qs
    if request.method == 'GET':
        context['days'] = filtered_set()
        context['filter'] = DayFilter()
    return render(request, 'workoutentry/day_list.html', context)


def filtered_set():
    month_ago = datetime.date.today() - datetime.timedelta(days=30)
    return Day.objects.filter(date__gt=month_ago)


class DayListView(ListView):
    model = Day
    context_object_name = 'days'

    def get(self, request, *args, **kwargs):
        _ = super().get(request, args, kwargs)

        context = {'days': self.get_queryset(),
                   'filter': DayFilter()}

        return render(request, 'workoutentry/day_list.html', context)

    def get_queryset(self):
        month_ago = datetime.date.today() - datetime.timedelta(days=30)
        return Day.objects.filter(date__gt=month_ago)


class DayUpdateView(UpdateView):
    model = Day
    success_url = '/days/'
    fields = ['date',
              'sleep',
              'sleep_quality',
              'fatigue',
              'motivation',
              'type',
              'comments']

    def post(self, request, *args, **kwargs):
        day = Day.objects.get(id=kwargs['pk'])
        print(request.POST)
        physio = None
        if 'kg' in request.POST:
            if KG.objects.filter(date=day.date):
                physio = KG.objects.get(date=day.date)
                physio.value = request.POST['value']
            else:
                physio = KG(date=day.date, value=request.POST['value'])
        elif 'fat' in request.POST:
            if FatPercentage.objects.filter(date=day.date):
                physio = FatPercentage.objects.get(date=day.date)
                physio.value = request.POST['value']
            else:
                physio = FatPercentage(date=day.date, value=request.POST['value'])
        elif 'hr' in request.POST:
            if RestingHeartRate.objects.filter(date=day.date):
                physio = RestingHeartRate.objects.get(date=day.date)
                physio.value = request.POST['value']
            else:
                physio = RestingHeartRate(date=day.date, value=request.POST['value'])
        elif 'sdnn' in request.POST:
            if SDNN.objects.filter(date=day.date):
                physio = SDNN.objects.get(date=day.date)
                physio.value = request.POST['value']
            else:
                physio = SDNN(date=day.date, value=request.POST['value'])
        elif 'rmssd' in request.POST:
            if RMSSD.objects.filter(date=day.date):
                physio = RMSSD.objects.get(date=day.date)
                physio.value = request.POST['value']
            else:
                physio = RMSSD(date=day.date, value=request.POST['value'])
        else:
            return super().post(request, args, kwargs)

        if physio is not None:
            physio.save()

        return HttpResponseRedirect(f'/days/{day.id}')


    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        from django.forms.widgets import TextInput
        form.fields['date'].widget = TextInput(attrs={'class': 'datepicker', 'placeholder': 'YYYY-MM-DD'})
        unique_types = Day.objects.values('type').distinct()
        unique_sleep_quality = Day.objects.values('sleep_quality').distinct()
        form.fields['type'] = forms.CharField(required=True,
                                              widget=Select(choices=[(u['type'], u['type']) for u in unique_types],
                                                            attrs={'class': 'form-control', 'id': 'type'}))

        form.fields['sleep_quality'] = forms.CharField(required=True,
                                              widget=Select(choices=[(u['sleep_quality'], u['sleep_quality']) for u in unique_sleep_quality],
                                                            attrs={'class': 'form-control', 'id': 'sleep_quality'}))
        return form


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
        return f'/days/{day_pk}'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        from django.forms.widgets import TextInput
        form.fields['date'].widget = TextInput(attrs={'class': 'datepicker', 'placeholder': 'YYYY-MM-DD'})
        return form