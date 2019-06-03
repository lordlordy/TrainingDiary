from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import json
from workoutentry.models import Workout, Day, RestingHeartRate, SDNN, RMSSD, KG, FatPercentage
import dateutil.parser
import datetime
import json
from django.contrib import messages


@login_required
def diary_upload(request):
    if request.method == 'POST':
        if 'document' in request.FILES:
            uploaded_file = request.FILES['document']
            upload_diary(request, uploaded_file)
        elif 'export' in request.POST:
            from_date = to_date = None
            try:
                from_date = dateutil.parser.parse(request.POST['from_date'])
            except ValueError as e:
                print(e)
            try:
                to_date = dateutil.parser.parse(request.POST['to_date'])
            except ValueError as e:
                print(e)
            json_str = diary_json_between_dates(from_date, to_date)
            response = HttpResponse(json_str, content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename=export.json'
            return response

    return render(request, 'workoutentry/diary_upload.html')



def upload_diary(request, uploaded_file):
    day_count = workout_count = kg_count = fat_count = hr_count = sdnn_count = rmssd_count = 0
    data = json.load(uploaded_file)
    for d in data['days']:
        date = dateutil.parser.parse(d['iso8601DateString'])
        if Day.objects.filter(date=date).exists():
            continue
        day = Day(date=date,
                  sleep=datetime.timedelta(hours=d['sleep']),
                  sleep_quality=d['sleepQuality'],
                  fatigue=d['fatigue'],
                  motivation=d['motivation'],
                  type=d['type'],
                  comments=d['comments'])

        day.save()
        day_count += 1

        if 'workouts' in d:
            for w in d['workouts']:
                equipment = w['equipmentName']
                if equipment == 'Not Set':
                    equipment = None
                workout = Workout(activity=w['activityString'],
                                  activity_type=w['activityTypeString'],
                                  equipment=equipment,
                                  day=day,
                                  duration=datetime.timedelta(seconds=w['seconds']),
                                  rpe=w['rpe'],
                                  tss=w['tss'],
                                  tss_method=w['tssMethod'],
                                  km=w['km'],
                                  kj=w['kj'],
                                  ascent_metres=w['ascentMetres'],
                                  reps=w['reps'],
                                  is_race=w['isRace'],
                                  cadence=w['cadence'],
                                  watts=w['watts'],
                                  watts_estimated=w['wattsEstimated'],
                                  heart_rate=w['hr'],
                                  is_brick=w['brick'],
                                  keywords=w['keywords'],
                                  comments=w['comments'])
                workout.save()
                workout_count += 1

    for d in data['restingHR']:
        date = dateutil.parser.parse(d['iso8601DateString'])
        if RestingHeartRate.objects.filter(date=date).exists():
            pass
        else:
            resting_hr = RestingHeartRate(date=date, value=round(d['value'], 1))
            resting_hr.save()
            hr_count += 1

    for d in data['restingSDNN']:
        date = dateutil.parser.parse(d['iso8601DateString'])
        if SDNN.objects.filter(date=date).exists():
            pass
        else:
            sdnn = SDNN(date=date, value=round(d['value'], 1))
            sdnn.save()
            sdnn_count += 1

    for d in data['restingRMSSD']:
        date = dateutil.parser.parse(d['iso8601DateString'])
        if RMSSD.objects.filter(date=date).exists():
            pass
        else:
            rmssd = RMSSD(date=date, value=round(d['value'], 1))
            rmssd.save()
            rmssd_count += 1

    for d in data['kg']:
        date = dateutil.parser.parse(d['iso8601DateString'])
        if KG.objects.filter(date=date).exists():
            pass
        else:
            kg = KG(date=date, value=round(d['value'], 1))
            kg.save()
            kg_count += 1

    for d in data['fatPercentage']:
        date = dateutil.parser.parse(d['iso8601DateString'])
        if FatPercentage.objects.filter(date=date).exists():
            pass
        else:
            fat_percentage = FatPercentage(date=date, value=round(d['value'], 1))
            fat_percentage.save()
            fat_count += 1

    messages.success(request, f'Data Uploaded')
    messages.info(request, f'Day Count: {day_count}')
    messages.info(request, f'Workout Count: {workout_count}')
    messages.info(request, f'KG Count: {kg_count}')
    messages.info(request, f'Fat Percentage Count: {fat_count}')
    messages.info(request, f'Resting Heart Rate Count: {hr_count}')
    messages.info(request, f'Resting SDNN Count: {sdnn_count}')
    messages.info(request, f'Resting rMSSD Count: {rmssd_count}')


def diary_json_between_dates(from_date=None, to_date=None):
    if from_date is None and to_date is None:
        days = Day.objects.all()
        kg = KG.objects.all()
        fat_percent = FatPercentage.objects.all()
        resting_hr = RestingHeartRate.objects.all()
        sdnn = SDNN.objects.all()
        rmssd = RMSSD.objects.all()
    elif from_date is None:
        days = Day.objects.filter(date__lte=to_date)
        kg = KG.objects.filter(date__lte=to_date)
        fat_percent = FatPercentage.objects.filter(date__lte=to_date)
        resting_hr = RestingHeartRate.objects.filter(date__lte=to_date)
        sdnn = SDNN.objects.filter(date__lte=to_date)
        rmssd = RMSSD.objects.filter(date__lte=to_date)
    elif to_date is None:
        days = Day.objects.filter(date__gte=from_date)
        kg = KG.objects.filter(date__gte=from_date)
        fat_percent = FatPercentage.objects.filter(date__gte=from_date)
        resting_hr = RestingHeartRate.objects.filter(date__gte=from_date)
        sdnn = SDNN.objects.filter(date__gte=from_date)
        rmssd = RMSSD.objects.filter(date__gte=from_date)
    else:
        days = Day.objects.filter(date__gte=from_date, date__lte=to_date)
        kg = KG.objects.filter(date__gte=from_date, date__lte=to_date)
        fat_percent = FatPercentage.objects.filter(date__gte=from_date, date__lte=to_date)
        resting_hr = RestingHeartRate.objects.filter(date__gte=from_date, date__lte=to_date)
        sdnn = SDNN.objects.filter(date__gte=from_date, date__lte=to_date)
        rmssd = RMSSD.objects.filter(date__gte=from_date, date__lte=to_date)

    training_diary_dd = {"athleteName": "Steven Lord",
                         "Generated By" : "Django Training Diary",
                         "Included": "Days",
                         "days": [d.data_dictionary() for d in days],
                         "kg": [d.data_dictionary() for d in kg],
                         "fatPercent": [d.data_dictionary() for d in fat_percent],
                         "restingHR": [d.data_dictionary() for d in resting_hr],
                         "sdnn": [d.data_dictionary() for d in sdnn],
                         'rmssd': [d.data_dictionary() for d in rmssd]}

    return json.dumps(training_diary_dd, indent=4)

