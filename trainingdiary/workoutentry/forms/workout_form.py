from django import forms
from django.forms.widgets import Select
from workoutentry.training_data import TrainingDataManager


class WorkoutEditForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tdm = TrainingDataManager()

        self.fields['activity'] = forms.CharField(required=True,
                                                  widget=Select(choices=[(a, a) for a in tdm.activities()],
                                                                attrs={'class': 'form-control', 'id': 'activity'}))
        self.fields['activity_type'] = forms.CharField(required=True, label='Type',
                                                       widget=Select(choices=[(a, a) for a in tdm.activity_types()],
                                                                     attrs={'class': 'form-control', 'id': 'activity_type'}))
        self.fields['tss_method'] = forms.CharField(required=True,
                                                    widget=Select(choices=[(a, a) for a in tdm.tss_methods()],
                                                                  attrs={'class': 'form-control', 'id': 'tss_method'}))
        self.fields['equipment'] = forms.CharField(required=False,
                                                   widget=Select(choices=[(a, a) for a in tdm.equipment_types()],
                                                                 attrs={'class': 'form-control', 'id': 'equipment'}))

        self.fields['seconds'] = forms.CharField(required=False)
        self.fields['km'] = forms.DecimalField(required=False)
        self.fields['ascent_metres'] = forms.IntegerField(required=False, label="Ascent")
        self.fields['rpe'] = forms.DecimalField(required=False)
        self.fields['heart_rate'] = forms.IntegerField(required=False)
        self.fields['reps'] = forms.IntegerField(required=False)
        self.fields['tss'] = forms.IntegerField(required=False)
        self.fields['cadence'] = forms.IntegerField(required=False)
        self.fields['kj'] = forms.IntegerField(required=False)
        self.fields['watts'] = forms.IntegerField(required=False)
        self.fields['watts_estimated_yes_no'] = forms.CharField(required=True, label="Watts Estimated?",
                                                                widget=Select(choices=[(a, a) for a in ["Yes","No"]],
                                                                              attrs={'class': 'form-control', 'id': 'watts'}))
        self.fields['is_race_yes_no'] = forms.CharField(required=True, label="Race?",
                                                        widget=Select(choices=[(a, a) for a in ["Yes","No"]],
                                                                      attrs={'class': 'form-control', 'id': 'race'}))
        self.fields['is_brick_yes_no'] = forms.CharField(required=True, label="Brick?",
                                                         widget=Select(choices=[(a, a) for a in ["Yes","No"]],
                                                                       attrs={'class': 'form-control', 'id': 'brick'}))
        self.fields['keywords'] = forms.CharField(required=False)
        self.fields['comments'] = forms.CharField(required=False, widget=forms.Textarea())