from django.db import models


class Workout(models.Model):
    activity = models.CharField(max_length=15)
    activity_type = models.CharField(max_length=15)
    date = models.DateField()
    duration = models.DurationField()
    rpe = models.DecimalField(max_digits=3, decimal_places=1)
    tss = models.DecimalField(max_digits=5, decimal_places=1)
    tss_method = models.CharField(max_length=15)
    km = models.DecimalField(max_digits=5, decimal_places=1)
    kj = models.IntegerField()
    ascent_metres = models.IntegerField()
    reps = models.IntegerField()
    keywords = models.TextField()
    is_race = models.BooleanField()
    cadence = models.IntegerField()
    watts = models.IntegerField()
    watts_estimated = models.BooleanField()
    heart_rate = models.IntegerField()
    is_brick = models.BooleanField()
    comments = models.TextField()
