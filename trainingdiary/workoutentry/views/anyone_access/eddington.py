
from workoutentry.modelling.eddington import EddingtonNumberProcessor, AnnualEddingtonNumberProcessor, MonthlyEddingtonNumberProcessor
from workoutentry.modelling.processor import NoOpProcessor
from workoutentry.views.anyone_access.time_series import TimeSeriesAccess


# todo this can probably be removed and switched to TimeSeriesAccess directly
class EddingtonNumberCalculation(TimeSeriesAccess):

    URL = "/eddington/calculation/"

    def required_post_fields(self):
        return ['json']

    def get_processor(self, dd):
        if dd['eddington_type'] == 'Lifetime':
            return EddingtonNumberProcessor()
        elif dd['eddington_type'] == 'Annual':
            return AnnualEddingtonNumberProcessor()
        elif dd['eddington_type'] == 'Monthly':
            return MonthlyEddingtonNumberProcessor()
        else:
            return NoOpProcessor()