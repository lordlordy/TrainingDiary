from django import forms
from django.forms.widgets import Select
from workoutentry.training_data import TrainingDataManager


class ReadingEditForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tdm = TrainingDataManager()

        self.fields['reading_type'] = forms.CharField(required=False,
                                              widget=Select(choices=[(a, a) for a in tdm.reading_types()],
                                                            attrs={'class': 'form-control', 'id': 'type'}))


        self.fields['value'] = forms.DecimalField()
