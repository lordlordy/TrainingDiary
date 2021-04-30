import json
from datetime import timedelta

from django.http import JsonResponse

from dateutil import parser

from workoutentry.training_data import TrainingDataManager
from workoutentry.views.json.response import TrainingDiaryResponse
from workoutentry.views.training_diary_resource import TrainingDiaryResource


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


class ChoiceListForType(TrainingDiaryResource):

    URL = '/field/choices/'

    def required_post_fields(self):
        return ['type']

    def call_resource(self, request):
        type = request.POST['type']
        tdm = TrainingDataManager()

        choices = list()
        if type == 'activity':
            choices = tdm.activities()
        elif type == 'activityType':
            choices = tdm.activity_types()
        elif type == 'equipment':
            choices = tdm.equipment_types()
        elif type == 'tssMethod':
            choices = tdm.tss_methods()
        elif type == 'dayType':
            choices = tdm.day_types()

        response = TrainingDiaryResponse()
        response.add_data('choices', sorted([{'text': c, 'id': c} for c in choices], key=lambda c: c["text"]))

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


class BaseSave(TrainingDiaryResource):

    def required_post_fields(self):
        return ['json']

    def _int_fields(self) -> set:
        return {}

    def _float_fields(self) -> set:
        return {}

    def _extra_processing(self, data) -> bool:
        return False

    def _process_data(self, json_data) -> (dict, set):
        data = json.loads(json_data)
        dd = dict()
        errors = set()
        for d in data:
            field_name = d['name']
            value = d['value']
            if field_name in self._int_fields():
                try:
                    dd[field_name] = int(value)
                except ValueError as e:
                    errors.add(f"Invalid {field_name} value: {e}")
            elif field_name in self._float_fields():
                try:
                    dd[field_name] = float(value)
                except ValueError as e:
                    errors.add(f"Invalid {field_name} value: {e}")
            elif field_name in {"can_record_for_day", "can_record_in_workout"}:
                dd[field_name] = value.lower() == 'yes'

            elif not self._extra_processing(data):
                dd[field_name] = value
        return dd, errors


class SaveDay(BaseSave):

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


class SaveNewReadings(BaseSave):

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