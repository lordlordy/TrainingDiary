from django import forms
from django.forms.widgets import Select, TimeInput, TextInput, HiddenInput, SelectMultiple
from studentTSB.database import occurrence_states, DatabaseManager


class SelectForm(forms.Form):

    def __init__(self, name, choices, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[name] = forms.CharField(required=True, label='',
                                            widget=SelectMultiple(choices=choices, attrs={'class': 'form-control',
                                                                                          'id': name}))


class SelectSingleForm(forms.Form):

    def __init__(self, name, choices, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[name] = forms.CharField(required=True, label='',
                                            widget=Select(choices=choices, attrs={'class': 'form-control', 'id': name}))


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
        self.fields['duration'] = forms.TimeField(required=True, widget=TimeInput(attrs={'placeholder': 'hh:mm:ss'}))
        states = DatabaseManager().event_occurrence_states()
        self.fields['state_id'] = forms.CharField(required=True, label='state',
                                                  widget=Select(choices=[(s.id, s.name) for s in states],
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
        states = DatabaseManager().event_occurrence_states()
        self.fields['state_id'] = forms.CharField(required=True,
                                                  widget=Select(choices=[(s.id, s.name) for s in states],
                                                                attrs={'class': 'form-control', 'id': 'status'}))
        self.fields['comments'] = forms.CharField(required=False, widget=forms.Textarea())


class ReadingTypeEditForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id'] = forms.IntegerField(required=False, widget=HiddenInput())
        self.fields['id'].widget.attrs['readonly'] = 'readonly'
        self.fields['name'] = forms.CharField(required=True)
        self.fields['min_value'] = forms.DecimalField(required=True)
        self.fields['max_value'] = forms.DecimalField(required=True)


class ReadingEditForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id'] = forms.IntegerField(required=False, widget=HiddenInput())
        self.fields['id'].widget.attrs['readonly'] = 'readonly'
        self.fields['player_event_occurrence_id'] = forms.IntegerField(required=False, widget=HiddenInput())
        self.fields['player_event_occurrence_id'].widget.attrs['readonly'] = 'readonly'
        reading_types = DatabaseManager().reading_types()
        self.fields['name'] = forms.CharField(required=True,
                                              widget=Select(choices=[(r.id, r.name) for r in reading_types],
                                                            attrs={'class': 'form-control', 'id': 'reading_type'}))

        self.fields['value'] = forms.DecimalField(required=True)


class EventOccurrenceStatusEditForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'] = forms.CharField(required=True, label='',
                                              widget=TextInput(attrs={'placeholder': 'New Event Occurrence State'}))