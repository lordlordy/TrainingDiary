import json
from datetime import timedelta

from django.http import JsonResponse

from dateutil import parser

from workoutentry.training_data import TrainingDataManager
from workoutentry.views.json.response import TrainingDiaryResponse
from workoutentry.views.training_diary_resource import TrainingDiaryResource
from workoutentry.views.utilities.utilities import BaseJSONForm


class NextDiaryDate(TrainingDiaryResource):

    URL = '/data/next_diary_date/'

    def call_resource(self, request):
        response = TrainingDiaryResponse()
        last_date = TrainingDataManager().latest_date()
        d = parser.parse(last_date).date()
        next_date = d + timedelta(1)
        response.add_data('next_date', next_date)

        return JsonResponse(data=response.as_dict())


class DataForDate(TrainingDiaryResource):

    URL = '/data/for_dates/'

    def required_post_fields(self):
        return ['from_date', 'to_date', 'data_type']

    def call_resource(self, request):
        response = TrainingDiaryResponse()
        tdm = TrainingDataManager()
        instances = []
        if request.POST['data_type'] == 'Day':
            instances = tdm.days_between(request.POST['from_date'], request.POST['to_date'])
        elif request.POST['data_type'] == 'Reading':
            instances = tdm.readings_between(request.POST['from_date'], request.POST['to_date'])
        elif request.POST['data_type'] == 'Workout':
            instances = tdm.workouts_between(request.POST['from_date'], request.POST['to_date'])

        response.add_data('instances', [i.data_dictionary() for i in instances])

        return JsonResponse(data=response.as_dict())


class ReadingsLeftForDay(TrainingDiaryResource):

    URL = '/readings/left_for_date/'

    def required_post_fields(self):
        return ['date']

    def call_resource(self, request):
        readings = TrainingDataManager().reading_types_unused_for_date(request.POST['date'])

        response = TrainingDiaryResponse()
        response.add_data('readings', readings)

        return JsonResponse(data=response.as_dict())


class SaveDay(TrainingDiaryResource):

    URL = '/save/day/'

    def required_post_fields(self):
        return ['date', 'day_type', 'comments']

    def call_resource(self, request):
        target_date = request.POST['date']
        response = TrainingDiaryResponse()
        tdm = TrainingDataManager()

        if tdm.day_exists(target_date):
            tdm.update_day(target_date, request.POST['day_type'], request.POST['comments'])
            response.add_message(response.MSG_INFO, f"Day updated for {target_date}")
        else:
            tdm.save_day(target_date, request.POST['day_type'], request.POST['comments'])
            response.add_message(response.MSG_INFO, f"New day added for {target_date}")

        response.add_data('day', tdm.day_for_date(target_date).data_dictionary())

        return JsonResponse(data=response.as_dict())


class SaveNewReadings(TrainingDiaryResource):

    URL = '/readings/new/save/'

    def required_post_fields(self):
        return ['json', 'date']

    def call_resource(self, request):
        date = request.POST['date']
        readings = list()
        tdm = TrainingDataManager()
        for reading in json.loads(request.POST['json']):
            tdm.save_reading(date, reading['reading'], reading['value'])
            readings.append(reading['reading'])

        readings_saved = list()
        for r in readings:
            readings_saved.append(tdm.reading_for_date_and_type(date, r)[0].data_dictionary())

        response = TrainingDiaryResponse()
        response.add_message(response.MSG_INFO, f"{len(readings)} saved: {', '.join(readings)}")
        response.add_data('readings', readings_saved)
        return JsonResponse(data=response.as_dict())


class SaveWorkout(BaseJSONForm):

    URL = '/workout/save/'

    COMMON_FIELDS = {'activity', 'activity_type', 'equipment', 'seconds', 'rpe', 'tss', 'tss_method', 'km', 'kj', 'ascent_metres',
                  'reps', 'is_race', 'cadence', 'watts', 'watts_estimated', 'heart_rate', 'is_brick', 'keywords', 'comments'}
    UPDATE_FIELDS = {'primary_key'} | COMMON_FIELDS
    NEW_FIELDS = {'date'} | COMMON_FIELDS

    def required_post_fields(self):
        return ['json']

    def call_resource(self, request):
        response = TrainingDiaryResponse()
        dd, errors = self._process_data(request.POST['json'])
        [response.add_message(response.MSG_ERROR, e) for e in errors]

        tdm = TrainingDataManager()
        primary_key = tdm.workout_primary_key(dd['date'], dd['workout_number'])
        try:
            if 'primary_key' not in dd or dd['primary_key'] == "":
                # new workout
                lastrowid = tdm.save_workout(**self._filtered_dict(dd, self.NEW_FIELDS))
                response.add_message(response.MSG_INFO, f"New workout saved")
                response.add_data('workout', tdm.workout_for_rowid(lastrowid)[0].data_dictionary())
            elif primary_key == dd['primary_key']:
                # update workout
                tdm.update_workout(**self._filtered_dict(dd, self.UPDATE_FIELDS))
                response.add_message(response.MSG_INFO, f"Workout updated")
                response.add_data('workout', tdm.workout_for_primary_key(primary_key)[0].data_dictionary())
            else:
                # changed the date. Need a new workout to get primary_keys right
                old_key = dd['primary_key']
                tdm.delete_workout_for_primary_key(old_key)
                response.add_data('removed_primary_key', old_key)
                lastrowid = tdm.save_workout(**self._filtered_dict(dd, self.NEW_FIELDS))
                workout = tdm.workout_for_rowid(lastrowid)[0]
                response.add_message(response.MSG_INFO, f"Workout date changed so old workout deleted and new one added. Remove {old_key} and added {workout.primary_key}")
                response.add_data('workout', workout.data_dictionary())
        except TypeError as e:
            response.set_status(response.ERROR)
            response.add_message(response.MSG_ERROR, str(e))

        return JsonResponse(data=response.as_dict())

    def _filtered_dict(self, dd, filter) -> (dict, set):
        new_dd = dict()
        errors = set()
        for k in filter:
            if k in {'is_race', 'is_brick', 'watts_estimated'}:
                new_dd[k] = 1 if k in dd else 0
            elif k == 'seconds':
                parts = dd[k].split(":")
                if len(parts) != 3:
                    errors.add(f"Invalid time format. Expecting three parts hh:mm:ss but got {len(parts)}")
                try:
                    new_dd[k] = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                except Exception:
                    errors.add(f"Invalid time format: {dd[k]}")
            elif k not in dd:
                errors.add(f"Missing field: {k}")
            else:
                new_dd[k] = dd[k]

        return new_dd

    def _int_fields(self) -> set:
        return {}

    def _float_fields(self) -> set:
        return {}

    def _yes_no_boolean_fields(self) -> set:
        return {"can_record_for_day", "can_record_in_workout"}

    def _extra_processing(self, data) -> bool:
        return False


class DeleteWorkout(TrainingDiaryResource):

    URL = '/workout/delete/'

    def required_post_fields(self):
        return ['primary_key']

    def call_resource(self, request):
        response = TrainingDiaryResponse()
        try:
            tdm = TrainingDataManager()
            tdm.delete_workout_for_primary_key(request.POST['primary_key'])
            response.set_status(response.SUCCESS)
            response.add_data('primary_key', request.POST['primary_key'])
            response.add_message(response.MSG_INFO, f"Workout Deleted: {request.POST['primary_key']}")
        except Exception as e:
            response.set_status(response.ERROR)
            response.add_message(response.MSG_ERROR, f"Delete failed: {str(e)}")

        return JsonResponse(data=response.as_dict())


class DeleteReading(TrainingDiaryResource):

    URL = '/reading/delete/'

    def required_post_fields(self):
        return ['primary_key']

    def call_resource(self, request):
        response = TrainingDiaryResponse()
        try:
            tdm = TrainingDataManager()
            tdm.delete_reading_for_primary_key(request.POST['primary_key'])
            response.set_status(response.SUCCESS)
            response.add_data('primary_key', request.POST['primary_key'])
            response.add_message(response.MSG_INFO, f"Reading Deleted: {request.POST['primary_key']}")
        except Exception as e:
            response.set_status(response.ERROR)
            response.add_message(response.MSG_ERROR, f"Delete failed: {str(e)}")

        return JsonResponse(data=response.as_dict())