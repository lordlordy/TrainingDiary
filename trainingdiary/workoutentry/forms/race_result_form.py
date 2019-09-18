from django import forms
from django.forms.widgets import Select
from workoutentry.training_data import TrainingDataManager


class RaceResultEditForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tdm = TrainingDataManager()

        self.fields['type'] = forms.CharField(required=False,
                                              widget=Select(choices=[(a, a) for a in tdm.race_types()],
                                                            attrs={'class': 'form-control', 'id': 'race_type'}))
        self.fields['brand'] = forms.CharField(required=False,
                                              widget=Select(choices=[(a, a) for a in tdm.race_brands()],
                                                            attrs={'class': 'form-control', 'id': 'race_brand'}))
        self.fields['distance'] = forms.CharField(required=False,
                                              widget=Select(choices=[(a, a) for a in tdm.race_distances()],
                                                            attrs={'class': 'form-control', 'id': 'race_distance'}))
        self.fields['category'] = forms.CharField(required=False,
                                                    widget=Select(choices=[(a, a) for a in tdm.race_categories()],
                                                                  attrs={'class': 'form-control', 'id': 'race_categorie'}))

        self.fields['name'] = forms.CharField()
        self.fields['overall_position'] = forms.IntegerField()
        self.fields['category_position'] = forms.IntegerField()
        self.fields['swim_seconds'] = forms.IntegerField()
        self.fields['t1_seconds'] = forms.IntegerField()
        self.fields['bike_seconds'] = forms.IntegerField()
        self.fields['t2_seconds'] = forms.IntegerField()
        self.fields['run_seconds'] = forms.IntegerField()
        self.fields['swim_km'] = forms.DecimalField()
        self.fields['bike_km'] = forms.DecimalField()
        self.fields['run_km'] = forms.DecimalField()
        self.fields['comments'] = forms.CharField(required=False, widget=forms.Textarea())
        self.fields['race_report'] = forms.CharField(required=False, widget=forms.Textarea())
