from datetime import date

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
                a_dd = totals.get(activity, {'km': 0, 'seconds': 0, 'tss': 0})
                a_dd['km'] += dd['km']
                a_dd['seconds'] += dd['seconds']
                a_dd['tss'] += dd['tss']
                totals[activity] = a_dd
            v['name'] = yr
            years.append(v)
        years.append(totals)
        # response.add_data('summary', summary)
        response.add_data('years', years)
        return JsonResponse(data=response.as_dict())


class TSBData(TrainingDiaryResource):

    URL = '/training/data/canned/'

    def required_post_fields(self):
        return ['year', 'activity', 'graph']

    def call_resource(self, request):
        response = TrainingDiaryResponse()
        tms = TimeSeriesManager()
        graph = request.POST['graph']
        activity = request.POST['activity']
        year_str = request.POST['year']
        title_components = [year_str if year_str != 'Total' else "All Time", activity if activity != "Total" else "All Activitivies"]

        if year_str == 'Total':
            tp = None
        else:
            year = int(year_str)
            tp = TimePeriod(date(year,1,1), date(year,12,31))

        if graph == 'tss':
            title_components.append("Training Stress Balance")
            values = tms.time_series(requested_time_period=tp,
                                     activity='All' if activity == "Total" else activity,
                                     activity_type='All',
                                     equipment='All',
                                     measure='tss',
                                     day_aggregation_method=DayAggregator.SUM)
        elif graph == 'duration':
            title_components.append("Duration")
            values = tms.time_series(requested_time_period=tp,
                                     activity='All' if activity == "Total" else activity,
                                     activity_type='All',
                                     equipment='All',
                                     measure='hours',
                                     day_aggregation_method=DayAggregator.SUM)
        elif graph == 'km':
            title_components.append("KM")
            values = tms.time_series(requested_time_period=tp,
                                     activity='All' if activity == "Total" else activity,
                                     activity_type='All',
                                     equipment='All',
                                     measure='km',
                                     day_aggregation_method=DayAggregator.SUM)
        else:
            values = dict()

        response.add_data('chart_title', " ".join(title_components))
        response.add_data('time_series', values)
        return JsonResponse(data=response.as_dict())