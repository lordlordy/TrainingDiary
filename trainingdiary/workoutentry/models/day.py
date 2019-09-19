import dateutil.parser
import functools
import operator

class Day:

    def __init__(self, *args):
        self.date = dateutil.parser.parse(args[0]).date()
        self.day_type = args[1]
        self.comments = args[2]

        from workoutentry.training_data import TrainingDataManager
        self.readings = TrainingDataManager().readings_for_date(self.date)
        self.reading_count = len(self.readings)
        rDict = dict()

        for r in self.readings:
            rDict[r.reading_type] = r.value

        if 'sleep' in rDict:
            self.sleep = rDict['sleep']

        if 'sleepQualityScore' in rDict:
            self.sleepQualityScore = rDict['sleepQualityScore']

        if 'fatigue' in rDict:
            self.fatigue = rDict['fatigue']

        if 'motivation' in rDict:
            self.motivation = rDict['motivation']

        if 'restingHR' in rDict:
            self.restingHR = int(rDict['restingHR'])

        if 'SDNN' in rDict:
            self.SDNN = rDict['SDNN']

        if 'rMSSD' in rDict:
            self.rMSSD = rDict['rMSSD']

        self.workouts = TrainingDataManager().workouts_on_date(self.date)
        self.workout_count = len(self.workouts)
        if self.workout_count > 0:
            self.tss = functools.reduce(operator.add, [w.tss for w in self.workouts])
            self.training_duration = functools.reduce(operator.add, [w.seconds for w in self.workouts])


    def __str__(self):
        return str(self.date )+ ' ~ ' + self.day_type + ' ~ ' + self.comments

    def workout_types(self):
        result = set()
        for w in self.workouts:
            result = result.union(w.workout_types)
        return result


    def data_dictionary(self):
        return {'date': self.date, 'day_type': self.day_type, 'comments': self.comments}