# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from datetime import timedelta





# class RaceResult(models.Model):
#     primary_key = models.CharField(max_length=32, primary_key=True)
#     date = models.DateField()
#     race_number = models.IntegerField()
#     type = models.CharField(max_length=16)
#     brand = models.CharField(max_length=16)
#     distance = models.CharField(max_length=16)
#     name = models.CharField(max_length=64)
#     category = models.CharField(max_length=16)
#     overall_position = models.IntegerField()
#     category_position = models.IntegerField()
#     swim_seconds = models.IntegerField()
#     t1_seconds = models.IntegerField()
#     bike_seconds = models.IntegerField()
#     t2_seconds = models.IntegerField()
#     run_seconds = models.IntegerField()
#     swim_km = models.FloatField()
#     bike_km = models.FloatField()
#     run_km = models.FloatField()
#     comments = models.TextField()
#     race_report = models.TextField()
#     last_save = models.DateField(blank=True, null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'RaceResult'
#
#
# class Reading(models.Model):
#     primary_key = models.CharField(max_length=32, primary_key=True)
#     date = models.ForeignKey(Day, models.DO_NOTHING, db_column='date')
#     type = models.CharField(max_length=16)
#     value = models.FloatField()
#
#     class Meta:
#         managed = False
#         db_table = 'Reading'
#
#
#
# class Workout(models.Model):
#     primary_key = models.CharField(max_length=32, primary_key=True)
#     date = models.DateField()
#     workout_number = models.IntegerField()
#     activity = models.CharField(max_length=16)
#     activity_type = models.CharField(max_length=16)
#     equipment = models.CharField(max_length=32)
#     seconds = models.IntegerField()
#     rpe = models.FloatField()
#     tss = models.IntegerField()
#     tss_method = models.CharField(max_length=16)
#     km = models.FloatField()
#     kj = models.IntegerField()
#     ascent_metres = models.IntegerField()
#     reps = models.IntegerField()
#     is_race = models.BooleanField()
#     cadence = models.IntegerField(blank=True, null=True)
#     watts = models.IntegerField()
#     watts_estimated = models.BooleanField()
#     heart_rate = models.IntegerField()
#     is_brick = models.BooleanField()
#     keywords = models.TextField()
#     comments = models.TextField()
#     last_save = models.DateField(blank=True, null=True)
#
#     # @property
#     # def day(self):
#     #     return Day.objects.filter(date=self.date)
#
#     class Meta:
#         managed = False
#         db_table = 'Workout'
