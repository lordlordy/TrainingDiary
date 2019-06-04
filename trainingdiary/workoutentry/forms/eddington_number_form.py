from django import forms
from django.forms.widgets import Select
from workoutentry.data_warehouse import DataWarehouse


class PopularEddingtonNumberForm(forms.Form):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['popular'] = forms.CharField(required=True, label='',
                                                 widget=Select(
                                                     choices=[(k, k) for k in DataWarehouse.popular_numbers],
                                                     attrs={'class': 'form-control', 'id': 'popular'}))


class EddingtonNumberForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        dw = DataWarehouse.instance()
        col_choices = [(c,c) for c in dw.float_column_names() + dw.int_column_names() ]

        self.fields['activity'] = forms.CharField(required=True,
                                                  widget=Select(
                                                      choices=[(a, a) for a in dw.activities()],
                                                      attrs={'class': 'form-control', 'id': 'activity'}))
        self.fields['activity_type'] = forms.CharField(required=True, label='Type',
                                                       widget=Select(
                                                           choices=[(a, a) for a in dw.activity_types()],
                                                           attrs={'class': 'form-control', 'id': 'activity_type'}))
        self.fields['equipment'] = forms.CharField(required=True,
                                                   widget=Select(
                                                       choices=[(a, a) for a in dw.equipment()],
                                                       attrs={'class': 'form-control', 'id': 'equipment'}))
        self.fields['period'] = forms.CharField(required=True,
                                                   widget=Select(
                                                       choices=[(i, i) for i in DataWarehouse.periods],
                                                       attrs={'class': 'form-control', 'id': 'period'}))
        self.fields['to_date'] = forms.CharField(required=True, label='To Date?',
                                                   widget=Select(
                                                       choices=[('No', 'No'), ('Yes', 'Yes')],
                                                       attrs={'class': 'form-control', 'id': 'to_date'}))
        self.fields['aggregation'] = forms.CharField(required=False, label='Aggregation',
                                                     widget=Select(
                                                         choices=[(i, i) for i in DataWarehouse.aggregators],
                                                         attrs={'class': 'form-control', 'id': 'aggregation'}))
        self.fields['rolling'] = forms.CharField(required=True, label='Rolling?',
                                                 widget=Select(
                                                     choices=[('No', 'No'), ('Yes', 'Yes')],
                                                     attrs={'class': 'form-control', 'id': 'rolling'}))
        self.fields['rolling_periods'] = forms.IntegerField(required=True, initial=0, min_value=0,
                                                            label='#')
        self.fields['rolling_aggregation'] = forms.CharField(required=False, label='Aggregation',
                                                     widget=Select(
                                                         choices=[(i, i) for i in DataWarehouse.aggregators],
                                                         attrs={'class': 'form-control', 'id': 'rolling_aggregation'}))
        self.fields['measure'] = forms.CharField(required=True,
                                                 widget=Select(
                                                     choices=col_choices,
                                                     attrs={'class': 'form-control', 'id': 'measure'}))

        self.fields['day_of_week'] = forms.CharField(required=True, label='Day',
                                                     widget=Select(
                                                         choices=[(d, d) for d in DataWarehouse.days_of_week],
                                                         attrs={'class': 'form-control', 'id': 'day_of_week'}))

        self.fields['month'] = forms.CharField(required=True,
                                               widget=Select(
                                                   choices=[(d, d) for d in DataWarehouse.months],
                                                   attrs={'class': 'form-control', 'id': 'month'}))

        self.fields['day_type'] = forms.CharField(required=True,
                                                  widget=Select(
                                                      choices=[(d, d) for d in dw.day_types()],
                                                      attrs={'class': 'form-control', 'id': 'day_type'}))