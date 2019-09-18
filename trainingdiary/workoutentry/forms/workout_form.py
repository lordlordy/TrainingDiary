from django import forms
from django.forms.widgets import Select
from workoutentry.training_data import TrainingDataManager


class WorkoutEditForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tdm = TrainingDataManager()

        self.fields['activity'] = forms.CharField(required=False,
                                              widget=Select(choices=[(a, a) for a in tdm.activities()],
                                                            attrs={'class': 'form-control', 'id': 'activity'}))
        self.fields['activity_type'] = forms.CharField(required=False,
                                              widget=Select(choices=[(a, a) for a in tdm.activity_types()],
                                                            attrs={'class': 'form-control', 'id': 'activity_type'}))
        self.fields['tss_method'] = forms.CharField(required=False,
                                              widget=Select(choices=[(a, a) for a in tdm.tss_methods()],
                                                            attrs={'class': 'form-control', 'id': 'tss_method'}))
        self.fields['equipment'] = forms.CharField(required=False,
                                                    widget=Select(choices=[(a, a) for a in tdm.equipment_types()],
                                                                  attrs={'class': 'form-control', 'id': 'equipment'}))

        self.fields['seconds'] = forms.CharField()
        self.fields['km'] = forms.DecimalField()
        self.fields['ascent_metres'] = forms.IntegerField(label="Ascent")
        self.fields['rpe'] = forms.DecimalField()
        self.fields['heart_rate'] = forms.IntegerField()
        self.fields['reps'] = forms.IntegerField()
        self.fields['tss'] = forms.IntegerField()
        self.fields['cadence'] = forms.IntegerField()
        self.fields['kj'] = forms.IntegerField()
        self.fields['watts'] = forms.IntegerField()
        self.fields['watts_estimated'] = forms.BooleanField()
        self.fields['is_race'] = forms.BooleanField()
        self.fields['is_brick'] = forms.BooleanField()
        self.fields['keywords'] = forms.CharField(required=False)
        self.fields['comments'] = forms.CharField(required=False, widget=forms.Textarea())