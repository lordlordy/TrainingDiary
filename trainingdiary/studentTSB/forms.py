from django import forms
from django.forms.widgets import Select, TimeInput, TextInput, HiddenInput, SelectMultiple
from studentTSB.database import occurrence_states


class SelectForm(forms.Form):

    def __init__(self, name, choices, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[name] = forms.CharField(required=True, label='',
                                            widget=SelectMultiple(choices=choices, attrs={'class': 'form-control',
                                                                                          'id': name}))


class TeamEditForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id'] = forms.IntegerField(required=False, widget=HiddenInput())
        self.fields['name'] = forms.CharField(required=True, label='',
                                              widget=TextInput(attrs={'placeholder': 'New Team Name'}))


class EventEditForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['id'] = forms.IntegerField(required=False, widget=HiddenInput())
        self.fields['id'].widget.attrs['readonly'] = 'readonly'

        self.fields['team_id'] = forms.IntegerField(required=False, widget=HiddenInput())
        self.fields['team_id'].widget.attrs['readonly'] = 'readonly'

        self.fields['name'] = forms.CharField(required=True)
        self.fields['start_time'] = forms.TimeField(required=True, widget=TimeInput())
        self.fields['end_time'] = forms.TimeField(required=True, widget=TimeInput())
        self.fields['estimated_rpe'] = forms.DecimalField(required=True)

        self.fields['start_date'] = forms.DateField(required=False,
                                                    widget=TextInput(attrs={'class': 'datepicker',
                                                                            'placeholder': 'yyyy-mm-dd'}))
        self.fields['end_date'] = forms.DateField(required=False,
                                                  widget=TextInput(attrs={'class': 'datepicker',
                                                                            'placeholder': 'yyyy-mm-dd'}))

        freq_choices = ['weekly', 'one off']
        self.fields['frequency'] = forms.CharField(required=True,
                                                   widget=Select(choices=[(a, a) for a in freq_choices],
                                                                attrs={'class': 'form-control', 'id': 'frequency'}))


class PersonEditForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id'] = forms.IntegerField(required=False, widget=HiddenInput())
        self.fields['id'].widget.attrs['readonly'] = 'readonly'
        self.fields['first_name'] = forms.CharField(required=True)
        self.fields['surname'] = forms.CharField(required=True)
        self.fields['known_as'] = forms.CharField(required=True)
        self.fields['email'] = forms.CharField(required=True)


class PlayerEditForm(PersonEditForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dob'] = forms.DateField(required=False,
                                             widget=TextInput(attrs={'class': 'datepicker',
                                                                     'placeholder': 'yyyy-mm-dd'}))


class CoachEditForm(PersonEditForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PlayerEventOccurrenceForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id'] = forms.IntegerField(required=False, widget=HiddenInput())
        self.fields['id'].widget.attrs['readonly'] = 'readonly'
        self.fields['rpe'] = forms.DecimalField(required=True)
        self.fields['duration'] = forms.TimeField(required=True, widget=TimeInput())
        self.fields['status'] = forms.CharField(required=True,
                                                widget=Select(choices=[(a, a) for a in occurrence_states],
                                                              attrs={'class': 'form-control', 'id': 'status'}))
        self.fields['comments'] = forms.CharField(required=False, widget=forms.Textarea())


class PersonalTrainingForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['player_id'] = forms.IntegerField(required=False, widget=HiddenInput())

        self.fields['date'] = forms.DateField(required=True,
                                              widget=TextInput(attrs={'class': 'datepicker',
                                                                      'placeholder': 'yyyy-mm-dd'}))
        self.fields['rpe'] = forms.DecimalField(required=False)
        self.fields['duration'] = forms.TimeField(required=True, widget=TimeInput())
        self.fields['status'] = forms.CharField(required=True,
                                                widget=Select(choices=[(a, a) for a in occurrence_states],
                                                              attrs={'class': 'form-control', 'id': 'status'}))
        self.fields['comments'] = forms.CharField(required=False, widget=forms.Textarea())
