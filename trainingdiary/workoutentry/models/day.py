from django.db import models
import datetime
from .physiological import KG, RestingHeartRate, FatPercentage, SDNN, RMSSD


class Day(models.Model):
    date = models.DateField(unique=True)
    sleep = models.DurationField(default=datetime.timedelta(hours=8))
    sleep_quality = models.CharField(max_length=15)
    fatigue = models.DecimalField(default=5.0, decimal_places=1, max_digits=4)
    motivation = models.DecimalField(default=5.0, decimal_places=1, max_digits=4)
    type = models.CharField(max_length=15)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.date.strftime('%Y-%m-%d')

    @property
    def workouts(self):
        from . import Workout
        return Workout.objects.filter(day=self)

    @property
    def number_of_workouts(self):
        return len(self.workouts)

    @property
    def training_duration(self):
        duration = datetime.timedelta()
        for w in self.workouts:
            duration += w.duration
        return duration

    @property
    def tss(self):
        tss = 0
        for w in self.workouts:
            tss += w.tss
        return int(tss)

    @property
    def kg(self):
        if KG.objects.filter(date=self.date).exists():
            return KG.objects.get(date=self.date).value
        else:
            return None

    @property
    def hr(self):
        if RestingHeartRate.objects.filter(date=self.date).exists():
            return RestingHeartRate.objects.get(date=self.date).value
        else:
            return None

    @property
    def fat_percentage(self):
        if FatPercentage.objects.filter(date=self.date).exists():
            return FatPercentage.objects.get(date=self.date).value
        else:
            return None

    @property
    def sdnn(self):
        if SDNN.objects.filter(date=self.date).exists():
            return SDNN.objects.get(date=self.date).value
        else:
            return None

    @property
    def rmssd(self):
        if RMSSD.objects.filter(date=self.date).exists():
            return RMSSD.objects.get(date=self.date).value
        else:
            return None