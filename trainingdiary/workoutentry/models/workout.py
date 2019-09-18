# from django.db import models
# from .day import Day
# import datetime#
import dateutil.parser
from datetime import timedelta


class Workout:

    def __init__(self, *args):

        self.primary_key = args[0]
        self.date = dateutil.parser.parse(args[1]).date()
        self.workout_number = args[2]
        self.activity = args[3]
        self.activity_type = args[4]
        self.equipment = args[5]
        self.seconds = timedelta(seconds=args[6])
        self.rpe = args[7]
        self.tss = args[8]
        self.tss_method = args[9]
        self.km = args[10]
        self.kj = args[11]
        self.ascent_metres = args[12]
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

    def __str__(self):
        return f'{self.date} ~ {self.workout_number}: {self.activity}:{self.activity_type}:{self.equipment} : {self.seconds}s'

    def data_dictionary(self):
        return {'primary_key': self.primary_key,
                'date': self.date,
                'workout_number': self.workout_number,
                'activity': self.activity,
                'activity_type': self.activity_type,
                'equipment': self.equipment,
                'seconds': self.seconds,
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