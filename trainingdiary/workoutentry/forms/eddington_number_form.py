from django import forms
from django.forms.widgets import Select
from workoutentry.models import (Workout, Day)
from workoutentry.data_warehouse import DataWarehouse


class EddingtonNumberForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        unique_activities = Workout.objects.values('activity').distinct()
        activity_choices = [('All', 'All')] + [(a['activity'], a['activity']) for a in unique_activities]
        unique_activity_types = Workout.objects.values('activity_type').distinct()
        activity_type_choices = [('All', 'All')] + [(a['activity_type'], a['activity_type']) for a in unique_activity_types]
        unique_equipment = [e for e in Workout.objects.values('equipment').distinct()
                            if e['equipment'] is not None and e['equipment'] != '']
        equipment_choices = [('All', 'All')] + [(a['equipment'], a['equipment']) for a in unique_equipment]

        period_choices = [('Day', 'Day'), ('Week', 'Week'), ('Month', 'Month')]

        dw = DataWarehouse.instance()
        col_choices = [(c,c) for c in dw.float_column_names() + dw.int_column_names() ]

        self.fields['activity'] = forms.CharField(required=True,
                                                  widget=Select(
                                                      choices=activity_choices,
                                                      attrs={'class': 'form-control', 'id': 'activity'}))
        self.fields['activity_type'] = forms.CharField(required=True,
                                                       widget=Select(
                                                           choices=activity_type_choices,
                                                           attrs={'class': 'form-control', 'id': 'activity_type'}))
        self.fields['equipment'] = forms.CharField(required=True,
                                                   widget=Select(
                                                       choices=equipment_choices,
                                                       attrs={'class': 'form-control', 'id': 'equipment'}))
        self.fields['period'] = forms.CharField(required=True,
                                                   widget=Select(
                                                       choices=period_choices,
                                                       attrs={'class': 'form-control', 'id': 'period'}))
        self.fields['measure'] = forms.CharField(required=True,
                                                 widget=Select(
                                                     choices=col_choices,
                                                     attrs={'class': 'form-control', 'id': 'measure'}))