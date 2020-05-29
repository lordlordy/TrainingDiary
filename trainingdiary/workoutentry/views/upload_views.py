from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import dateutil.parser
import json
from django.contrib import messages
from workoutentry.training_data import TrainingDataManager
from workoutentry.forms import DataImportForm, DataExportForm

@login_required
def import_export(request):
    return render(request, 'workoutentry/data_import_export.html', {'import_form': DataImportForm(),
                                                                    'export_form': DataExportForm()})

@login_required
def data_import(request):
    if request.method == 'POST':
        if 'document' in request.FILES:
            uploaded_file = request.FILES['document']
            upload_diary(request, uploaded_file,
                         request.POST['import_choice'] == 'Merge',
                         request.POST['import_choice'] == 'Overwrite')

    return render(request, 'workoutentry/data_import_export.html', {'import_form': DataImportForm(),
                                                                    'export_form': DataExportForm()})


@login_required
def data_export(request):
    if request.method == 'POST':
        from_date = to_date = None
        try:
            from_date = dateutil.parser.parse(request.POST['export_from_date']).date()
        except:
            messages.error(request, f'Please select a from date')
        try:
            to_date = dateutil.parser.parse(request.POST['export_to_date']).date()
        except:
            messages.error(request, f'Please select a to date')
        if from_date is not None and to_date is not None:
            json_str = diary_json_between_dates(from_date, to_date)
            response = HttpResponse(json_str, content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename=export.json'
            return response

    return render(request, 'workoutentry/data_import_export.html', {'import_form': DataImportForm(),
                                                                    'export_form': DataExportForm()})


def upload_diary(request, uploaded_file, merge, overwrite):
    day_count = workout_count = reading_count = race_count = 0
    days_not_imported = []
    data = json.load(uploaded_file)
    tdm = TrainingDataManager()
    for d in data['Days']:
        date = dateutil.parser.parse(d['iso8601DateString']).date()
        day_exists = tdm.day_for_date(date) is not None
        if day_exists:
            if merge:
                pass
            elif overwrite:
                tdm.delete_day(date)
                messages.info(request, f'Day, workouts, readings and race results replaced for {date}')
            else:
                days_not_imported.append(str(date))
                continue

        # only save this if it doesn't exist OR we are overwriting
        if not day_exists or overwrite:
            tdm.save_day(date, d['type'], d['comments'])
            day_count += 1

        # from here only need to worry about merge. If it's overwite then the day has been removed if it exists so
        # can just save these. If it's not overwite or merge then it'll only get this far if no date exists.
        # thus if merge is true we then skip if workout exists

        if 'Workouts' in d:
            for w in d['Workouts']:
                if skip_workout(merge, date, w['workoutNumber']):
                    messages.info(request, f'''
                    Skipped workout {date}~#{w['workoutNumber']} {w["activity"]}:{w["activityType"]}:{w["equipment"]}:{w['seconds']}s
                    ''')
                    continue
                equipment = ""
                if 'equipment' in w:
                    equipment = w['equipment']
                    if equipment == 'Not Set':
                        equipment = ""

                tdm.save_workout(date, w['activity'],w['activityType'], equipment, w['seconds'], w['rpe'], w['tss'],
                                 w['tssMethod'], w['km'], w['kj'], w['ascentMetres'], w['reps'], w['isRace'],
                                 w['cadence'], w['watts'], w['wattsEstimated'], w['heartRate'], w['isBrick'],
                                 w['keywords'], w['comments'])
                workout_count += 1

        if 'Readings' in d:
            for r in d['Readings']:
                if skip_reading(merge, date, r['type']):
                    continu
                tdm.save_reading(date, r['type'], r['value'])
                reading_count += 1

    if 'RaceResults' in data:
        for rr in data['RaceResults']:
            date = dateutil.parser.parse(rr['iso8601DateString']).date()
            existing_result = tdm.race_result_for_date_and_number(date, rr['raceNumber'])
            if existing_result is not None:
                # have an existing result
                if overwrite:
                    tdm.delete_race_result(date, rr['raceNumber'])
                    messages.info(request, f'This race result has been replaced: {existing_result}')
                else:
                    # don't upload this
                    messages.info(request, f"Race report not imported: {rr['iso8601DateString']} - {rr['name']}")
                    continue

            tdm.save_race_result(date, rr['raceNumber'], rr['type'], rr['brand'], rr['distance'], rr['name'],
                                 rr['category'], rr['overallPosition'], rr['categoryPosition'], rr['swimSeconds'],
                                 rr['t1Seconds'], rr['bikeSeconds'], rr['t2Seconds'], rr['runSeconds'], rr['swimKM'],
                                 rr['bikeKM'], rr['runKM'], rr['comments'], rr['raceReport'])
            race_count += 1

    messages.success(request, f'Data Uploaded')
    messages.info(request, f'Day Count: {day_count}')
    messages.info(request, f'Workout Count: {workout_count}')
    messages.info(request, f'Reading Count: {reading_count}')
    messages.info(request, f'Race Result Count: {race_count}')
    if len(days_not_imported) > 0:
        messages.info(request, f'Dates not imported: {days_not_imported}')


def diary_json_between_dates(from_date, to_date):
    tdm = TrainingDataManager()
    days = tdm.days_between(from_date, to_date)
    race_results = tdm.race_results_between(from_date, to_date)

    training_diary_dd = {"athleteName": "Steven Lord",
                         "Generated By" : "Django Training Diary",
                         "JSONVersion": "WorkoutEditor_v1",
                         "Days": [d.json_dictionary() for d in days],
                         "RaceResults": [r.json_dictionary() for r in race_results]
                         }

    return json.dumps(training_diary_dd, indent=4)


def skip_workout(merge, date, workout_number):
    if not merge:
        return False
    existing_workout = TrainingDataManager().workout_for_date_and_number(date, workout_number)
    return len(existing_workout) > 0


def skip_reading(merge, date, reading_type):
    if not merge:
        return False
    existing_reading = TrainingDataManager().reading_for_date_and_type(date, reading_type)
    return len(existing_reading) > 0