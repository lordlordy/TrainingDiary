import numpy as np

from workoutentry.modelling.data_definition import SeriesDefinition
from workoutentry.modelling.processor import AbstractProcessor
from workoutentry.modelling.time_period import TimePeriod


class EddingtonNumberProcessor(AbstractProcessor):

    def __init__(self):
        self.ed_num = 0
        self.plus_one = 0
        self.contributors_to_next = np.array([])

    def no_op(self):
        return False

    def title_component(self):
        return 'Eddington Number'

    def adjusted_time_period(self, tp) -> TimePeriod:
        return tp

    def series_definitions(self, base_measure, base_series_definition):
        dd = super().series_definitions(base_measure, base_series_definition)
        dd['ed_num'] = SeriesDefinition(measure='ed_num', underlying_measure=base_measure)
        dd['plus_one'] = SeriesDefinition(measure='plus_one', underlying_measure=base_measure)
        dd['contributor'] = SeriesDefinition(measure='contributor', underlying_measure=base_measure)
        return dd

    def process(self, df):
        self.contributors_to_next = np.array([])

        df['ed_num'] = np.nan
        df['plus_one'] = np.nan
        df['contributor'] = np.nan

        df.sort_index(inplace=True)

        for i, row in df.iterrows():
            self._check_and_reset(i, row)
            v = row[0]
            if v >= self.ed_num + 1:
                # this contributes to LTD
                self.contributors_to_next = np.append(self.contributors_to_next, v)
                self.plus_one = (self.ed_num + 1) - self.contributors_to_next.size
                if self.plus_one == 0:
                    self.ed_num += 1
                    # remove non contributors as edd num increased
                    self.contributors_to_next = self.contributors_to_next[self.contributors_to_next >= self.ed_num + 1]
                    # recalc +1
                    self.plus_one = (self.ed_num + 1) - self.contributors_to_next.size

                row['ed_num'] = self.ed_num
                row['plus_one'] = self.plus_one
                row['contributor'] = round(v, 1)


        # drop the value col
        # df = df.drop(df.columns[0], axis=1)

        return df

    def _check_and_reset(self, index, row):
        pass


class AnnualEddingtonNumberProcessor(EddingtonNumberProcessor):

    def __init__(self):
        super().__init__()
        self.current_year = None

    def title_component(self):
        return 'Annual Eddington Number'

    def series_definitions(self, base_measure, base_series_definition):
        dd = super().series_definitions(base_measure, base_series_definition)
        dd['annual_ed_num'] = SeriesDefinition(measure='annual_ed_num', underlying_measure=base_measure)
        dd['annual_plus_one'] = SeriesDefinition(measure='annual_plus_one', underlying_measure=base_measure)
        return dd

    def process(self, df):
        self.current_year = df.index[0].year
        df['annual_ed_num'] = np.nan
        df['annual_plus_one'] = np.nan
        return super().process(df)

    def _check_and_reset(self, index, row):
        if index.year != self.current_year:
            row['annual_ed_num'] = self.ed_num
            row['annual_plus_one'] = self.plus_one
            self.current_year = index.year
            self.ed_num = 0
            self.contributors_to_next = np.array([])


class MonthlyEddingtonNumberProcessor(EddingtonNumberProcessor):

    ED_NUM = 'monthly_ed_num'
    PLUS_ONE = 'monthly_plus_one'

    def __init__(self):
        super().__init__()
        self.current_month = None

    def title_component(self):
        return 'Monthly Eddington Number'

    def series_definitions(self, base_measure, base_series_definition):
        dd = super().series_definitions(base_measure, base_series_definition)
        dd[self.ED_NUM] = SeriesDefinition(measure=self.ED_NUM, underlying_measure=base_measure)
        dd[self.PLUS_ONE] = SeriesDefinition(measure=self.PLUS_ONE, underlying_measure=base_measure)
        return dd

    def process(self, df):
        self.current_month = df.index[0].month
        df[self.ED_NUM] = np.nan
        df[self.PLUS_ONE] = np.nan
        return super().process(df)

    def _check_and_reset(self, index, row):
        if index.month != self.current_month:
            row[self.ED_NUM] = self.ed_num
            row[self.PLUS_ONE] = self.plus_one
            self.current_month = index.month
            self.ed_num = 0
            self.contributors_to_next = np.array([])


def temp():
    def eddington_history(self, time_series):
        ltd_history = []
        annual_history = []
        annual_summary = []
        monthly_history = []
        monthly_summary = []
        ltd_contributors_to_next = np.array([])
        this_years_annual_contributors_to_next = np.array([])
        this_months_contributors_to_next = np.array([])

        ed_num = 0
        annual_ed_num = 0
        annual_plus_one = 0
        monthly_ed_num = 0
        monthly_plus_one = 0
        current_year = time_series.index[0].year
        current_month = time_series.index[0].month

        time_series.sort_index(inplace=True)

        for i, v in time_series.iteritems():

            if i.month != current_month:
                monthly_summary.append((f'{current_year}-{current_month:02}', monthly_ed_num, monthly_plus_one))
                # reset all the monthly stuff
                current_month = i.month
                monthly_ed_num = 0
                this_months_contributors_to_next = np.array([])

            if i.year != current_year:
                annual_summary.append((current_year, annual_ed_num, annual_plus_one))
                # reset all the annual stuff
                current_year = i.year
                annual_ed_num = 0
                this_years_annual_contributors_to_next = np.array([])

            if v >= ed_num + 1:
                # this contributes to LTD
                ltd_contributors_to_next = np.append(ltd_contributors_to_next, v)
                plus_one = (ed_num + 1) - ltd_contributors_to_next.size
                if plus_one == 0:
                    ed_num += 1
                    # remove non contributors as edd num increased
                    ltd_contributors_to_next = ltd_contributors_to_next[ltd_contributors_to_next >= ed_num+1]
                    # recalc +1
                    plus_one = (ed_num + 1) - ltd_contributors_to_next.size

                ltd_history.append((str(i.date()), ed_num, plus_one, round(v, 1)))

            if v >= annual_ed_num + 1:
                # this contributes to annual
                this_years_annual_contributors_to_next = np.append(this_years_annual_contributors_to_next, v)
                annual_plus_one = (annual_ed_num + 1) - this_years_annual_contributors_to_next.size
                if annual_plus_one == 0:
                    annual_ed_num += 1
                    this_years_annual_contributors_to_next = this_years_annual_contributors_to_next[this_years_annual_contributors_to_next >= annual_ed_num+1]
                    # recalc +1
                    annual_plus_one = (annual_ed_num + 1) - this_years_annual_contributors_to_next.size
                annual_history.append((str(i.date()), annual_ed_num, annual_plus_one, round(v, 1)))

            if v >= monthly_ed_num + 1:
                # this contributes to monthly
                this_months_contributors_to_next = np.append(this_months_contributors_to_next, v)
                monthly_plus_one = (monthly_ed_num + 1) - this_months_contributors_to_next.size
                if monthly_plus_one == 0:
                    monthly_ed_num += 1
                    this_months_contributors_to_next = this_months_contributors_to_next[this_months_contributors_to_next >= monthly_ed_num + 1]
                    monthly_plus_one = (monthly_ed_num + 1) - this_months_contributors_to_next.size
                monthly_history.append((str(i.date()), monthly_ed_num, monthly_plus_one, round(v, 1)))

        annual_summary.append((current_year, annual_ed_num, annual_plus_one))
        monthly_summary.append((f'{current_year}-{current_month:02}', monthly_ed_num, monthly_plus_one))

        return ed_num, ltd_history, annual_history, annual_summary, monthly_history, monthly_summary