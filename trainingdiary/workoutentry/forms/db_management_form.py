from django import forms
from django.forms.widgets import Select, TextInput


class DBManagementForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['export_from_date'] = forms.DateField(required=False,
                                                          widget=TextInput(attrs={'class': 'datepicker',
                                                                                  'placeholder': 'yyyy-mm-dd'}))

        self.fields['export_to_date'] = forms.DateField(required=False,
                                                        widget=TextInput(attrs={'class': 'datepicker',
                                                                                'placeholder': 'yyyy-mm-dd'}))

        self.fields['update_warehouse_date'] = forms.DateField(required=False, label='Update from',
                                                               widget=TextInput(attrs={'class': 'datepicker',
                                                                                       'placeholder': 'yyyy-mm-dd'}))

        choices = [('New', 'Import new days only'),
                   ('Merge', 'Best effort merge'),
                   ('Overwrite', 'Overwrite duplicates')]

        self.fields['import_choice'] = forms.CharField(required=True,
                                                       widget=Select(choices=choices,
                                                                     attrs={'class': 'form-control',
                                                                            'id': 'import_choice'}))
