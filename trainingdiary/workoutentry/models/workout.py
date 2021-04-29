import dateutil.parser
from datetime import timedelta


class Workout:

    default_args = []

    def __init__(self, *args):
        from . import Constants

        self.primary_key = args[0]
        self.date_str = args[1]
        self.date = dateutil.parser.parse(args[1]).date()
        self.workout_number = args[2]
        self.activity = args[3]
        self.activity_type = args[4]
        self.equipment = args[5]
        self.__seconds = args[6]
        self.seconds = timedelta(seconds=args[6])
        self.rpe = args[7]
        self.rpe_tss = (100/49) * self.rpe * self.rpe * (self.seconds.total_seconds() / 3600)
        self.tss = args[8]
        self.tss_method = args[9]
        self.km = args[10]
        self.miles = self.km * Constants.MILES_PER_KM
        self.kj = args[11]
        self.ascent_metres = args[12]
        self.ascent_feet = self.ascent_metres * Constants.FEET_PER_METRE
        self.reps = args[13]
        self.is_race = args[14]
        self.cadence = args[15]
        self.watts = args[16]
        self.watts_estimated = args[17]
        self.heart_rate = args[18]
        self.is_brick = args[19]
        self.keywords = args[20]
        self.comments = args[21]
        self.last_save = args[22]

        from . import WorkoutType

        self.workout_types = {WorkoutType.workout_type_for(),
                  WorkoutType.workout_type_for(activity_type=self.activity_type),
                  WorkoutType.workout_type_for(activity=self.activity),
                  WorkoutType.workout_type_for(activity=self.activity, activity_type=self.activity_type)}
        if self.equipment != "":
            e = self.equipment.replace(" ","")
            self.workout_types.add(WorkoutType.workout_type_for(equipment=e))
            self.workout_types.add(WorkoutType.workout_type_for(activity_type=self.activity_type, equipment=e))
            self.workout_types.add(WorkoutType.workout_type_for(activity=self.activity, equipment=e))
            self.workout_types.add(WorkoutType.workout_type_for(activity=self.activity,
                                                                activity_type=self.activity_type, equipment=e))

    def __str__(self):
        return f'{self.date} ~ {self.workout_number}: {self.activity}:{self.activity_type}:{self.equipment} : {self.seconds}s'

    def data_dictionary(self):
        return {'DT_RowId': self.primary_key,
                'primary_key': self.primary_key,
                'date': self.date,
                'workout_number': self.workout_number,
                'activity': self.activity,
                'activity_type': self.activity_type,
                'equipment': self.equipment,
                'seconds': self.__seconds,
                'rpe': self.rpe,
                'tss': self.tss,
                'tss_method': self.tss_method,
                'km': self.km,
                'kj': self.kj,
                'ascent_metres': self.ascent_metres,
                'reps': self.reps,
                'is_race': self.is_race,
                'cadence': self.cadence,
                'watts': self.watts,
                'watts_estimated': self.watts_estimated,
                'heart_rate': self.heart_rate,
                'is_brick': self.is_brick,
                'keywords': self.keywords,
                'comments': self.comments,
                'last_save': self.last_save}

    def json_dictionary(self):
        return {"DT_RowId": self.primary_key,
                "activity": self.activity,
                "isRace": self.is_race,
                "ascentMetres": self.ascent_metres,
                "rpe": self.rpe,
                "wattsEstimated": self.watts_estimated,
                "kj": self.kj,
                "heartRate": self.heart_rate,
                "km": self.km,
                "workoutNumber": self.workout_number,
                "keywords": self.keywords,
                "reps": self.reps,
                "isBrick": self.is_brick,
                "activityType": self.activity_type,
                "comments": self.comments,
                "watts": self.watts,
                "tssMethod": self.tss_method,
                "equipment": self.equipment,
                "tss": self.tss,
                "seconds": self.__seconds,
                "cadence": self.cadence}