from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json
from workoutentry.models import Workout, Day, RestingHeartRate, SDNN, RMSSD, KG, FatPercentage
import dateutil.parser
import datetime


@login_required
def diary_upload(request):
    if (request.method == 'POST')and ('document' in request.FILES):
        uploaded_file = request.FILES['document']
        data = json.load(uploaded_file)
        for d in data['days']:
            date = dateutil.parser.parse(d['iso8061DateString'])
            if Day.objects.filter(date=date).exists():
                print(f'{date} EXISTS!!')
                continue
            day = Day(date=date,
                      sleep=datetime.timedelta(hours=d['sleep']),
                      sleep_quality=d['sleepQuality'],
                      fatigue=d['fatigue'],
                      motivation=d['motivation'],
                      type=d['type'],
                      comments=d['comments'])

            day.save()
            print(day)

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
                    print(workout)
        for p in data['physiologicals']:
            date = dateutil.parser.parse(p['iso8061DateString'])
            print(date)
            if 'restingHR' in p:
                if p['restingHR'] is not None:
                    if RestingHeartRate.objects.filter(date=date).exists():
                        print('HR exists')
                    else:
                        resting_hr = RestingHeartRate(date=date, value=round(p['restingHR'],1))
                        resting_hr.save()
                        print(resting_hr)
            if 'restingSDNN' in p:
                if p['restingSDNN'] is not None:
                    if SDNN.objects.filter(date=date).exists():
                        print('SDNN exists')
                    else:
                        sdnn = SDNN(date=date, value=round(p['restingSDNN'],1))
                        sdnn.save()
                        print(sdnn)

            if 'restingRMSSD' in p:
                if p['restingRMSSD'] is not None:
                    if RMSSD.objects.filter(date=date):
                        print('RMSSD exists')
                    else:
                        rmssd = RMSSD(date=date, value=round(p['restingRMSSD'],1))
                        rmssd.save()
                        print(rmssd)

        for p in data['weights']:
            date = dateutil.parser.parse(p['iso8061DateString'])
            print(date)
            if 'kg' in p:
                if p['kg'] is not None and p['kg'] > 0.0:
                    if KG.objects.filter(date=date).exists():
                        print('KG exists')
                    else:
                        kg = KG(date=date, value=round(p['kg'],1))
                        kg.save()
                        print(kg)

            if 'fatPercent' in p:
                if p['fatPercent'] is not None and p['fatPercent'] > 0.0:
                    if FatPercentage.objects.filter(date=date).exists():
                        print('Fat% exists')
                    else:
                        fat_percentage = FatPercentage(date=date, value=round(p['fatPercent'],1))
                        fat_percentage.save()
                        print(fat_percentage)

    return render(request, 'workoutentry/diary_upload.html')