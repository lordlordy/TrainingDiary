from django.http import JsonResponse

from workoutentry.modelling.modelling_types import DayAggregator
from workoutentry.modelling.time_period import TimePeriod
from workoutentry.modelling.time_series import TimeSeriesManager
from workoutentry.training_data import TrainingDataManager
from workoutentry.views.json.response import TrainingDiaryResponse
from workoutentry.views.training_diary_resource import TrainingDiaryResource


class BikeSummary(TrainingDiaryResource):

    URL = '/bike/summary/'

    def call_resource(self, request):
        response = TrainingDiaryResponse()
        tdm = TrainingDataManager()
        summary = tdm.bike_summary()
        bikes = list()
        totals = {'name': 'Total'}
        for bike, years in summary.items():
            for year, value in years.items():
                y = totals.get(year, 0)
                y += value
                totals[year] = y
            years['name'] = bike
            bikes.append(years)
        bikes.append(totals)
        response.add_data('bikes', bikes)
        years = list()
        for k, v in summary.items():
            years = [y for y in sorted(v.keys(), reverse=True)]
            break
        response.add_data('years', years)

        return JsonResponse(data=response.as_dict())


class TrainingSummary(TrainingDiaryResource):

    URL = '/training/summary/'

    def call_resource(self, request):
        response = TrainingDiaryResponse()
        tdm = TrainingDataManager()
        summary = tdm.training_annual_summary()
        totals = {"name": 'Total'}
        years = list()
        for yr, v in summary.items():
            for activity, dd in v.items():
                a_dd = totals.get(activity, {'km': 0, 'seconds': 0})
                a_dd['km'] += dd['km']
                a_dd['seconds'] += dd['seconds']
                totals[activity] = a_dd
            v['name'] = yr
            years.append(v)
        years.append(totals)
        # response.add_data('summary', summary)
        response.add_data('years', years)
        return JsonResponse(data=response.as_dict())


class TSBData(TrainingDiaryResource):

    URL = '/training/tsb/'

    def call_resource(self, request):
        response = TrainingDiaryResponse()
        tms = TimeSeriesManager()
        values = tms.time_series(time_period=TimePeriod('2021-01-01', '2021-12-31'),
                                 activity='Swim',
                                 activity_type='All',
                                 equipment='All',
                                 measure='TSS',
                                 day_aggregation_method=DayAggregator.SUM)
        response.add_data('values', values)
        return JsonResponse(data=response.as_dict())