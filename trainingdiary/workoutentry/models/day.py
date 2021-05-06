import dateutil.parser
import functools
import operator


class Day:

    def __init__(self, *args):
        self.date_str = args[0]
        self.date = dateutil.parser.parse(args[0]).date()
        self.day_type = args[1]
        self.comments = args[2]

    def populate_readings(self):
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
            if self.sleepQualityScore < 0.2:
                self.sleep_quality = "Very Poor"
            elif self.sleepQualityScore < 0.4:
                self.sleep_quality = "Poor"
            elif self.sleepQualityScore < 0.6:
                self.sleep_quality= "Average"
            elif self.sleepQualityScore < 0.8:
                self.sleep_quality= "Good"
            else:
                self.sleep_quality= "Excellent"
        else:
            self.sleep_quality = "Average"

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

        if 'kg' in rDict:
            self.kg = rDict['kg']

        if 'fatPercentage' in rDict:
                self.fat_percentage = rDict['fatPercentage']

        # values for data warehouse. Want zero instead of null
        self.dw_sleep = rDict['sleep'] if 'sleep' in rDict else 0.0
        self.dw_sleepQualityScore = rDict['sleepQualityScore'] if 'sleepQualityScore' in rDict else 0.0
        self.dw_fatigue = rDict['fatigue'] if 'fatigue' in rDict else 0.0
        self.dw_motivation = rDict['motivation'] if 'motivation' in rDict else 0.0
        self.dw_restingHR = int(rDict['restingHR']) if 'restingHR' in rDict else 0.0
        self.dw_SDNN = rDict['SDNN'] if 'SDNN' in rDict else 0.0
        self.dw_rMSSD = rDict['rMSSD'] if 'rMSSD' in rDict else 0.0
        self.dw_kg = rDict['kg'] if 'kg' in rDict else 0.0
        self.dw_fatPercentage = rDict['fatPercentage'] if 'fatPercentage' in rDict else 0.0

    def populate_workouts(self):
        from workoutentry.training_data import TrainingDataManager
        self.workouts = TrainingDataManager().workouts_on_date(self.date)
        self.workout_count = len(self.workouts)
        if self.workout_count > 0:
            self.tss = functools.reduce(operator.add, [w.tss for w in self.workouts])
            self.training_duration = functools.reduce(operator.add, [w.seconds for w in self.workouts])
        swim_workouts = list(filter(lambda x: x.activity == 'Swim', self.workouts))
        bike_workouts = list(filter(lambda x: x.activity == 'Bike', self.workouts))
        run_workouts = list(filter(lambda x: x.activity == 'Run', self.workouts))
        self.swim_km = 0.0
        self.bike_km = 0.0
        self.run_km = 0.0
        if len(swim_workouts) > 0:
            self.swim_km = functools.reduce(operator.add, [w.km for w in swim_workouts])
        if len(bike_workouts) > 0:
            self.bike_km = functools.reduce(operator.add, [w.km for w in bike_workouts])
        if len(run_workouts) > 0:
            self.run_km = functools.reduce(operator.add, [w.km for w in run_workouts])


    def __str__(self):
        return str(self.date )+ ' ~ ' + self.day_type + ' ~ ' + self.comments

    def default_workout(self):
        workout_number = len(self.workouts) + 1
        primary_key = f"{self.date_str}-{workout_number}"
        from . import Workout
        w_args = [primary_key, self.date_str, workout_number, 'Swim', 'Squad', "",
                        0, 5.0, 0.0, 'RPE', 0.0, 0, 0, 0, 0, 0, 0, 1, 0, 0, "", "", ""]
        return Workout(*w_args)

    def workouts_of_type(self, workout_type):
        result = []
        for w in self.workouts:
            if workout_type in w.workout_types:
                result.append(w)
        return result

    def workout_types(self):
        result = set()
        for w in self.workouts:
            result = result.union(w.workout_types)
        return result

    def data_dictionary(self):
        return {'DT_RowId': self.date_str,
                'date': self.date_str,
                'day_type': self.day_type,
                'comments': self.comments}

    def json_dictionary(self):
        self.populate_readings()
        self.populate_workouts()
        return {'iso8601DateString': self.date_str,
                'type': self.day_type,
                'comments': self.comments,
                'Readings': [r.json_dictionary() for r in self.readings],
                'Workouts': [w.json_dictionary() for w in self.workouts]}

    def warehouse_dictionary(self, workout_type):
        workouts = self.workouts_of_type(workout_type)
        seconds = tss = ascent_metres = kj = reps = is_race = brick = watts_estimated = 0
        hours = km = miles = rpe = hr = watts = cadence = rpe_tss = 0.0

        if len(workouts) > 0:
            seconds = functools.reduce(operator.add, [w.seconds for w in workouts]).total_seconds()
            hours = seconds / 3600
            km = functools.reduce(operator.add, [w.km for w in workouts])
            miles = functools.reduce(operator.add, [w.miles for w in workouts])
            rpe = 0.0 if seconds == 0 else functools.reduce(operator.add, [w.rpe * w.seconds.total_seconds() for w in workouts]) / seconds
            hr = 0.0 if seconds == 0 else functools.reduce(operator.add, [w.heart_rate * w.seconds.total_seconds() for w in workouts]) / seconds
            watts = 0.0 if seconds == 0 else functools.reduce(operator.add, [w.watts * w.seconds.total_seconds() for w in workouts]) / seconds
            cadence = 0.0 if seconds == 0 else functools.reduce(operator.add, [w.cadence * w.seconds.total_seconds() for w in workouts]) / seconds
            tss = functools.reduce(operator.add, [w.tss for w in workouts])
            ascent_metres = functools.reduce(operator.add, [w.ascent_metres for w in workouts])
            kj = functools.reduce(operator.add, [w.kj for w in workouts])
            reps = functools.reduce(operator.add, [w.reps for w in workouts])
            is_race = 1 if functools.reduce(operator.or_, [w.is_race for w in workouts]) > 0 else 0
            brick = 1 if functools.reduce(operator.or_, [w.is_brick for w in workouts]) > 0 else 0
            watts_estimated = 1 if functools.reduce(operator.or_, [w.watts_estimated for w in workouts]) > 0 else 0
            rpe_tss = functools.reduce(operator.add, [w.rpe_tss for w in workouts])

        from workoutentry.data_warehouse import WarehouseColumn as W_Col
        from . import Constants

        return {W_Col(W_Col.date): f"'{self.date_str}'",
                W_Col(W_Col.year): f"'{self.date.year}'",
                W_Col(W_Col.year_week): f"'{self.date.isocalendar()[0]}-{self.date.isocalendar()[1]}'",
                W_Col(W_Col.year_for_week): f"'{self.date.isocalendar()[0]}'",
                W_Col(W_Col.year_month): f"'{self.date.year}-{self.date.month}'",
                W_Col(W_Col.year_quarter): f"'{self.date.year}-{(self.date.month-1)//3 + 1}'",
                W_Col(W_Col.day_of_week): f"'{self.date.strftime('%a')}'",
                W_Col(W_Col.month): f"'{self.date.strftime('%b')}'",
                W_Col(W_Col.week): f"'{self.date.isocalendar()[1]}'",
                W_Col(W_Col.quarter): f"'{(self.date.month-1)//3 + 1}'",
                W_Col(W_Col.day_type): f"'{self.day_type}'",
                W_Col(W_Col.fatigue): self.dw_fatigue,
                W_Col(W_Col.motivation): self.dw_motivation,
                W_Col(W_Col.sleep_seconds): int(self.dw_sleep * 3600),
                W_Col(W_Col.sleep_minutes): int(self.dw_sleep * 60),
                W_Col(W_Col.sleep_hours): self.dw_sleep,
                W_Col(W_Col.sleep_score): self.dw_sleep * self.dw_sleepQualityScore,
                W_Col(W_Col.sleep_quality): f"'{self.sleep_quality}'",
                W_Col(W_Col.sleep_quality_score): self.dw_sleepQualityScore,
                W_Col(W_Col.km): km,
                W_Col(W_Col.miles): miles,
                W_Col(W_Col.tss): tss,
                W_Col(W_Col.rpe): rpe,
                W_Col(W_Col.hr): hr,
                W_Col(W_Col.watts): watts,
                W_Col(W_Col.seconds): seconds,
                W_Col(W_Col.minutes): int(seconds / 60),
                W_Col(W_Col.hours): hours,
                W_Col(W_Col.ascent_metres): ascent_metres,
                W_Col(W_Col.ascent_feet): ascent_metres * Constants.FEET_PER_METRE,
                W_Col(W_Col.kj): kj,
                W_Col(W_Col.reps): reps,
                W_Col(W_Col.is_race): is_race,
                W_Col(W_Col.brick): brick,
                W_Col(W_Col.watts_estimated): watts_estimated,
                W_Col(W_Col.cadence): cadence,
                W_Col(W_Col.rpe_tss): rpe_tss,
                W_Col(W_Col.mph): 0.0 if hours == 0.0 else miles / hours,
                W_Col(W_Col.kph): 0.0 if hours == 0.0 else km / hours,
                W_Col(W_Col.ctl): 0.0,
                W_Col(W_Col.atl): 0.0,
                W_Col(W_Col.tsb): 0.0,
                W_Col(W_Col.rpe_ctl): 0.0,
                W_Col(W_Col.rpe_atl): 0.0,
                W_Col(W_Col.rpe_tsb): 0.0,
                W_Col(W_Col.monotony): 0.0,
                W_Col(W_Col.strain): 0.0,
                W_Col(W_Col.rpe_monotony): 0.0,
                W_Col(W_Col.rpe_strain): 0.0,
                W_Col(W_Col.kg): self.dw_kg,
                W_Col(W_Col.lbs): self.dw_kg * Constants.LBS_PER_KG,
                W_Col(W_Col.fat_percentage): self.dw_fatPercentage,
                W_Col(W_Col.resting_hr): self.dw_restingHR,
                W_Col(W_Col.sdnn): self.dw_SDNN,
                W_Col(W_Col.rmssd): self.dw_rMSSD,
                W_Col(W_Col.kg_recorded): 1 if self.dw_kg > 0.0 else 0,
                W_Col(W_Col.lbs_recorded): 1 if self.dw_kg > 0.0 else 0,
                W_Col(W_Col.fat_percentage_recorded): 1 if self.dw_fatPercentage > 0.0 else 0,
                W_Col(W_Col.resting_hr_recorded): 1 if self.dw_restingHR > 0.0 else 0,
                W_Col(W_Col.sdnn_recorded): 1 if self.dw_SDNN > 0.0 else 0,
                W_Col(W_Col.rmssd_recorded): 1 if self.dw_rMSSD > 0.0 else 0,
                W_Col(W_Col.sdnn_off): 0.0,
                W_Col(W_Col.sdnn_easy): 0.0,
                W_Col(W_Col.sdnn_hard): 0.0,
                W_Col(W_Col.rmssd_off): 0.0,
                W_Col(W_Col.rmssd_easy): 0.0,
                W_Col(W_Col.rmssd_hard): 0.0}