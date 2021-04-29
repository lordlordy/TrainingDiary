from django.http import JsonResponse

from workoutentry.training_data import TrainingDataManager


def table_edit_reading(request):

    action = request.POST.get('action', None)
    if action == 'edit':
        return edit_reading(request.POST)
    elif action == 'remove':
        return JsonResponse(data={'error': "delete not implemented"})
    else:
        return JsonResponse(data={'error': "invalid action"})


def edit_reading(post_dictionary):

    models_dict = parse_post_dictionary(post_dictionary)
    tdm = TrainingDataManager()
    response_dict = dict()
    data = list()
    field_errors_list = list()
    primary_key = None
    for k, v in models_dict.items():
        primary_key = k
        for field, value in v.items():
            if field == 'value':
                tdm.update_reading_for_primary_key(k,value)
            else:
                field_errors_list.append({'name': 'value', 'status': f"invalid field name: {field}"})

    if primary_key is not None:
        reading = tdm.reading_for_primary_key(primary_key)
        data.append(reading.data_dictionary())
    else:
        response_dict['error'] = "No primary key"

    if len(data) > 0:
        response_dict['data'] = data
    if len(field_errors_list) > 0:
        response_dict['fieldErrors'] = field_errors_list

    return JsonResponse(data=response_dict)


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


