from datetime import date

from django.http import JsonResponse

from workoutentry.modelling.modelling_types import DayAggregation, Aggregation, PandasPeriod, ReadingEnum
from workoutentry.modelling.period import Period
from workoutentry.modelling.processor import TSBProcessor, TimeSeriesProcessor
from workoutentry.modelling.rolling import RollingDefinition, NoOpRoller
from workoutentry.modelling.time_period import TimePeriod
from workoutentry.modelling.time_series import TimeSeriesManager
from workoutentry.modelling.data_definition import DataDefinition, SeriesDefinition
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


class ReadingSummary(TrainingDiaryResource):

    URL = '/reading/summary/'

    def call_resource(self, request):

        period_year = Period(pandas_period=PandasPeriod.Y_DEC,
                             aggregation=Aggregation.MEAN,
                             to_date=False,
                             incl_zeroes=False)

        series_definition = SeriesDefinition(period=period_year, rolling_definition=NoOpRoller())

        time_series_sets = list()

        for reading in ReadingEnum:
            dd = DataDefinition(measure=reading.value, day_aggregation_method=DayAggregation.MEAN)
            time_series_sets.append(TimeSeriesManager.TimeSeriesSet(data_definition=dd,
                                                                    series_definition=series_definition,
                                                                    processor=TimeSeriesProcessor.get_processor("No-op")))

        diary_time_period = TrainingDataManager().diary_time_period()
        # year summaries do need time period to be to year end
        diary_time_period.end = date(diary_time_period.end.year, 12, 31)
        tsl, errors = TimeSeriesManager().time_series_list(requested_time_period=diary_time_period, time_series_list=time_series_sets)

        if len(tsl) > 0:
            total_series = {'date': "Total"}
            for k in tsl[0].keys():
                if k != 'date':
                    entries = [d[k] for d in tsl]
                    year_count = sum([1 for e in entries if e > 0])
                    total_series[k] = 0 if year_count == 0 else sum(entries) / year_count
            tsl.append(total_series)

        for dd in tsl:
            dd['name'] = dd['date']

        response = TrainingDiaryResponse()
        [response.add_message(response.MSG_ERROR, e) for e in errors]
        response.add_data('time_series', tsl)

        return JsonResponse(data=response.as_dict())


class CannedGraph(TrainingDiaryResource):

    URL = '/training/data/canned/'

    def required_post_fields(self):
        return ['year', 'activity', 'graph']

    def call_resource(self, request):
        response = TrainingDiaryResponse()
        tms = TimeSeriesManager()
        graph = request.POST['graph']
        activity = request.POST['activity']
        year_str = self._normalise_year_str(request.POST['year'])
        yr_title = year_str if year_str != 'Total' else "All Time"

        if year_str == 'Total':
            tdm = TrainingDataManager()
            tp = tdm.diary_time_period()
        else:
            year = int(year_str)
            tp = TimePeriod(date(year,1,1), date(year,12,31))

        tss_list = list()
        if graph == 'tss':
            tss_list.append(TimeSeriesManager.TimeSeriesSet(data_definition=DataDefinition(activity='All' if activity == "Total" else activity,
                                                                                           activity_type='All',
                                                                                           equipment='All',
                                                                                           measure='tss',
                                                                                           day_aggregation_method=DayAggregation.SUM),
                                                            processor=TSBProcessor(7, 7, 42, 42)))
        elif graph == 'duration':
            duration_defn = DataDefinition(activity='All' if activity == "Total" else activity,
                                           activity_type='All',
                                           equipment='All',
                                           measure='hours',
                                           day_aggregation_method=DayAggregation.SUM)
            tss_list.append(TimeSeriesManager.TimeSeriesSet(data_definition=duration_defn))
            tss_list.append(TimeSeriesManager.TimeSeriesSet(data_definition=duration_defn, series_definition=SeriesDefinition(Period(), RollingDefinition(7, Aggregation.SUM))))
        elif graph == 'km':
            km_defn = DataDefinition(activity='All' if activity == "Total" else activity,
                                     activity_type='All',
                                     equipment='All',
                                     measure='km',
                                     day_aggregation_method=DayAggregation.SUM)
            tss_list.append(TimeSeriesManager.TimeSeriesSet(data_definition=km_defn))
            tss_list.append(TimeSeriesManager.TimeSeriesSet(data_definition=km_defn, series_definition=SeriesDefinition(Period(), RollingDefinition(7, Aggregation.SUM))))
        elif graph == 'reading':
            reading_defn = DataDefinition(activity='All',
                                          activity_type='All',
                                          equipment='All',
                                          measure=activity,
                                          day_aggregation_method=DayAggregation.MEAN)
            tss_list.append(TimeSeriesManager.TimeSeriesSet(data_definition=reading_defn))
            tss_list.append(TimeSeriesManager.TimeSeriesSet(data_definition=reading_defn, series_definition=SeriesDefinition(Period(), RollingDefinition(7, Aggregation.MEAN))))
        elif graph == 'bike':
            bike_defn = DataDefinition(activity='Bike',
                                       activity_type='All',
                                       equipment='All' if activity == 'Total' else activity,
                                       measure='km',
                                       day_aggregation_method=DayAggregation.SUM)
            tss_list.append(TimeSeriesManager.TimeSeriesSet(data_definition=bike_defn))
            tss_list.append(TimeSeriesManager.TimeSeriesSet(data_definition=bike_defn,
                                                            series_definition=SeriesDefinition(Period(), RollingDefinition(7, Aggregation.SUM))))
            tss_list.append(TimeSeriesManager.TimeSeriesSet(data_definition=bike_defn,
                                                            series_definition=SeriesDefinition(Period(PandasPeriod.Y_DEC, Aggregation.SUM, to_date=True))))

        if len(tss_list) > 0:
            values = tms.time_series_graph(requested_time_period=tp, time_series_list=tss_list)
        else:
            values = {'title': "No Data"}

        response.add_data('chart_title', f"{yr_title} {values['title']}")
        response.add_data('time_series', values)
        return JsonResponse(data=response.as_dict())

    def _normalise_year_str(self, year_str) -> str:
        if year_str == "Total":
            return year_str
        return year_str[:4]