from django.db import models
from mainsite.utils import ordinal
import datetime


class RaceResult(models.Model):
    date = models.DateField()

    type = models.CharField(max_length=24)
    brand = models.CharField(max_length=24)
    distance = models.CharField(max_length=24)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=24, blank=True, null=True)

    overall_position = models.IntegerField(blank=True, null=True)
    number_of_participants = models.IntegerField(blank=True, null=True)
    category_position = models.IntegerField(blank=True, null=True)
    number_in_category = models.IntegerField(blank=True, null=True)

    swim = models.DurationField(blank=True, null=True)
    t1 = models.DurationField(blank=True, null=True)
    bike = models.DurationField(blank=True, null=True)
    t2 = models.DurationField(blank=True, null=True)
    run = models.DurationField(blank=True, null=True)

    swim_km = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    bike_km = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    run_km = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)

    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.date} {self.brand} {self.name}'

    @property
    def total_time(self):
        total_time = datetime.timedelta(seconds=0)
        if self.swim is not None:
            total_time += self.swim
        if self.t1 is not None:
            total_time += self.t1
        if self.bike is not None:
            total_time += self.bike
        if self.t2 is not None:
            total_time += self.t2
        if self.run is not None:
            total_time += self.run
        return total_time

    @property
    def category_position_str(self):
        if self.category_position is not None and self.category is not None:
            return ordinal(self.category_position) + ' ' + self.category
        else:
            return ''

    @property
    def overall_position_str(self):
        if self.overall_position is not None:
            return ordinal(self.overall_position) + ' overall'
        else:
            return ''
