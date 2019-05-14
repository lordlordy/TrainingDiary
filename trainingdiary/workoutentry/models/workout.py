from django.db import models
from .day import Day


class Workout(models.Model):
    activity = models.CharField(max_length=15, default='Run')
    activity_type = models.CharField(max_length=15, default='Road')
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    duration = models.DurationField()
    rpe = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    tss = models.DecimalField(max_digits=5, decimal_places=1, default=50.0)
    tss_method = models.CharField(max_length=15, default='RPE')
    km = models.DecimalField(max_digits=5, decimal_places=1, default=0.0)
    kj = models.IntegerField(default=0.0)
    ascent_metres = models.IntegerField(default=0)
    reps = models.IntegerField(default=0, null=True)
    is_race = models.BooleanField(default=False)
    cadence = models.IntegerField(blank=True, null=True)
    watts = models.IntegerField(blank=True, null=True)
    watts_estimated = models.BooleanField(default=True)
    heart_rate = models.IntegerField(blank=True, null=True)
    is_brick = models.BooleanField(default=False)
    keywords = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.day.date) + ':' + self.activity

