from django import forms
from django.forms.widgets import Select
from workoutentry.training_data import TrainingDataManager


class RaceResultEditForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tdm = TrainingDataManager()

        self.fields['type'] = forms.CharField(required=True,
                                              widget=Select(choices=[(a, a) for a in tdm.race_types()],
                                                            attrs={'class': 'form-control', 'id': 'race_type'}))
        self.fields['brand'] = forms.CharField(required=True,
                                              widget=Select(choices=[(a, a) for a in tdm.race_brands()],
                                                            attrs={'class': 'form-control', 'id': 'race_brand'}))
        self.fields['distance'] = forms.CharField(required=True,
                                              widget=Select(choices=[(a, a) for a in tdm.race_distances()],
                                                            attrs={'class': 'form-control', 'id': 'race_distance'}))
        self.fields['category'] = forms.CharField(required=True,
                                                    widget=Select(choices=[(a, a) for a in tdm.race_categories()],
                                                                  attrs={'class': 'form-control', 'id': 'race_category'}))

        self.fields['name'] = forms.CharField(required=True)
        self.fields['overall_position'] = forms.IntegerField(required=False)
        self.fields['category_position'] = forms.IntegerField(required=False)
        self.fields['swim_seconds'] = forms.CharField(required=False)
        self.fields['t1_seconds'] = forms.CharField(required=False)
        self.fields['bike_seconds'] = forms.CharField(required=False)
        self.fields['t2_seconds'] = forms.CharField(required=False)
        self.fields['run_seconds'] = forms.CharField(required=False)
        self.fields['swim_km'] = forms.DecimalField(required=False)
        self.fields['bike_km'] = forms.DecimalField(required=False)
        self.fields['run_km'] = forms.DecimalField(required=False)
        self.fields['comments'] = forms.CharField(required=False)
        self.fields['race_report'] = forms.CharField(required=False, widget=forms.Textarea())
