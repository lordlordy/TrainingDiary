import json

from dateutil import parser

from workoutentry.views.training_diary_resource import TrainingDiaryResource


def parse_post_dictionary(post_dictionary):

    parse_dict = dict()
    for k, value in post_dictionary.items():
        if 'data' in k:
            components = k.split('[')
            statera_model_key = components[1][0:-1]
            value_dict = parse_dict.get(statera_model_key, dict())
            if value == 'false':
                value = False
            elif value == 'true':
                value = True
            value_dict[components[2][0:-1]] = value
            parse_dict[statera_model_key] = value_dict

    return parse_dict


class BaseJSONForm(TrainingDiaryResource):

    def _int_fields(self) -> set:
        return {}

    def _float_fields(self) -> set:
        return {}

    def _yes_no_boolean_fields(self) -> set:
        return {}

    def _date_fields(self) -> set:
        return {}

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
            elif field_name in self._yes_no_boolean_fields():
                dd[field_name] = value.lower() == 'yes'
            elif field_name in self._date_fields():
                try:
                    dd[field_name] = parser.parse(value).date()
                except Exception:
                    dd[field_name] = None
            else:
                dd[field_name] = value
        return dd, errors
