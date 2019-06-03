# Generated by Django 2.2.1 on 2019-06-03 19:18

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Day',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True)),
                ('sleep', models.DurationField(default=datetime.timedelta(0, 28800))),
                ('sleep_quality', models.CharField(max_length=15)),
                ('fatigue', models.DecimalField(decimal_places=1, default=5.0, max_digits=4)),
                ('motivation', models.DecimalField(decimal_places=1, default=5.0, max_digits=4)),
                ('type', models.CharField(max_length=15)),
                ('comments', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='FatPercentage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True)),
                ('value', models.DecimalField(decimal_places=1, max_digits=4)),
            ],
        ),
        migrations.CreateModel(
            name='KG',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True)),
                ('value', models.DecimalField(decimal_places=1, max_digits=4)),
            ],
        ),
        migrations.CreateModel(
            name='RaceResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('type', models.CharField(max_length=24)),
                ('brand', models.CharField(max_length=24)),
                ('distance', models.CharField(max_length=24)),
                ('name', models.CharField(max_length=100)),
                ('category', models.CharField(blank=True, max_length=24, null=True)),
                ('overall_position', models.IntegerField(blank=True, null=True)),
                ('number_of_participants', models.IntegerField(blank=True, null=True)),
                ('category_position', models.IntegerField(blank=True, null=True)),
                ('number_in_category', models.IntegerField(blank=True, null=True)),
                ('swim', models.DurationField(blank=True, null=True)),
                ('t1', models.DurationField(blank=True, null=True)),
                ('bike', models.DurationField(blank=True, null=True)),
                ('t2', models.DurationField(blank=True, null=True)),
                ('run', models.DurationField(blank=True, null=True)),
                ('swim_km', models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True)),
                ('bike_km', models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True)),
                ('run_km', models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True)),
                ('comments', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RestingHeartRate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True)),
                ('value', models.DecimalField(decimal_places=1, max_digits=4)),
            ],
        ),
        migrations.CreateModel(
            name='RMSSD',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True)),
                ('value', models.DecimalField(decimal_places=1, max_digits=4)),
            ],
        ),
        migrations.CreateModel(
            name='SDNN',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True)),
                ('value', models.DecimalField(decimal_places=1, max_digits=4)),
            ],
        ),
        migrations.CreateModel(
            name='Workout',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity', models.CharField(default='Run', max_length=15)),
                ('activity_type', models.CharField(default='Road', max_length=15)),
                ('equipment', models.CharField(blank=True, max_length=30, null=True)),
                ('duration', models.DurationField(default=datetime.timedelta(0, 3600))),
                ('rpe', models.DecimalField(decimal_places=1, default=5.0, max_digits=3)),
                ('tss', models.DecimalField(decimal_places=1, default=50.0, max_digits=5)),
                ('tss_method', models.CharField(default='RPE', max_length=15)),
                ('km', models.DecimalField(decimal_places=1, default=0.0, max_digits=5)),
                ('kj', models.IntegerField(blank=True, default=0.0, null=True)),
                ('ascent_metres', models.IntegerField(blank=True, default=0, null=True)),
                ('reps', models.IntegerField(blank=True, default=0, null=True)),
                ('is_race', models.BooleanField(default=False)),
                ('cadence', models.IntegerField(blank=True, default=0, null=True)),
                ('watts', models.IntegerField(blank=True, default=0, null=True)),
                ('watts_estimated', models.BooleanField(default=True)),
                ('heart_rate', models.IntegerField(blank=True, default=0, null=True)),
                ('is_brick', models.BooleanField(default=False)),
                ('keywords', models.TextField(blank=True, null=True)),
                ('comments', models.TextField(blank=True, null=True)),
                ('day', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workoutentry.Day')),
            ],
        ),
    ]
