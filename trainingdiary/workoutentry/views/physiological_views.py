from django.shortcuts import render
from workoutentry.models import RestingHeartRate, SDNN, RMSSD, KG, FatPercentage
from workoutentry.forms import PhysiologicalSearchForm
import datetime


def physiologicals_view(request):
    if request.method == 'POST':
        from_date = request.POST['from']
        to_date = request.POST['to']
        if len(from_date) > 0 and len(to_date) > 0:
            kg, fat, hr, sdnn, rmssd = get_data_between(from_date, to_date)
        elif len(from_date) > 0:
            kg, fat, hr, sdnn, rmssd = get_data_after(from_date)
        elif len(to_date) > 0:
            kg, fat, hr, sdnn, rmssd = get_data_before(to_date)
        else:
            kg, fat, hr, sdnn, rmssd = get_all()
    else:
        month_ago = datetime.date.today() - datetime.timedelta(days=30)
        kg, fat, hr, sdnn, rmssd = get_data_after(month_ago)

    context = {'kg': kg,
               'fat_percentage': fat,
               'hr': hr,
               'sdnn': sdnn,
               'rmssd': rmssd,
               'form': PhysiologicalSearchForm()}

    return render(request, 'workoutentry/physiologicals.html', context)


def get_data_after(from_date):
    kg = KG.objects.filter(date__gte=from_date)
    hr = RestingHeartRate.objects.filter(date__gte=from_date)
    sdnn = SDNN.objects.filter(date__gte=from_date)
    rmssd = RMSSD.objects.filter(date__gte=from_date)
    fat = FatPercentage.objects.filter(date__gte=from_date)
    return kg, fat, hr, sdnn, rmssd


def get_data_before(to_date):
    kg = KG.objects.filter(date__lte=to_date)
    hr = RestingHeartRate.objects.filter(date__lte=to_date)
    sdnn = SDNN.objects.filter(date__lte=to_date)
    rmssd = RMSSD.objects.filter(date__lte=to_date)
    fat = FatPercentage.objects.filter(date__lte=to_date)
    return kg, fat, hr, sdnn, rmssd


def get_data_between(from_date, to_date):
    kg = KG.objects.filter(date__gte=from_date, date__lte=to_date)
    hr = RestingHeartRate.objects.filter(date__gte=from_date, date__lte=to_date)
    sdnn = SDNN.objects.filter(date__gte=from_date, date__lte=to_date)
    rmssd = RMSSD.objects.filter(date__gte=from_date, date__lte=to_date)
    fat = FatPercentage.objects.filter(date__gte=from_date, date__lte=to_date)
    return kg, fat, hr, sdnn, rmssd

def get_all():
    kg = KG.objects.all()
    hr = RestingHeartRate.objects.all()
    sdnn = SDNN.objects.all()
    rmssd = RMSSD.objects.all()
    fat = FatPercentage.objects.all()
    return kg, fat, hr, sdnn, rmssd
