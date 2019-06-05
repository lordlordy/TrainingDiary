from django import forms
from django.forms.widgets import TextInput


class PhysiologicalSearchForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['from'] = forms.DateField(required=False, label='',
                                              widget=TextInput(attrs={'class': 'datepicker',
                                                                      'placeholder': 'FROM: yyyy-mm-dd'}))
        self.fields['to'] = forms.DateField(required=False, label='',
                                            widget=TextInput(attrs={'class': 'datepicker',
                                                                    'placeholder': 'TO: yyyy-mm-dd'}))


