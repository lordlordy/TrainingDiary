from django import forms
from django.forms.widgets import Select, TextInput, SelectMultiple
from workoutentry.data_warehouse import WarehouseColumn, DataWarehouse


class DataImportForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        choices = [('New', 'Import new days only'),
                   ('Merge', 'Best effort merge'),
                   ('Overwrite', 'Overwrite duplicates')]

        self.fields['import_choice'] = forms.CharField(required=True, widget=Select(choices=choices,
                                                                                    attrs={'class': 'form-control',
                                                                                           'id': 'import_choice'}))


class DataExportForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['export_from_date'] = forms.DateField(required=False,
                                                          widget=TextInput(attrs={'class': 'datepicker',
                                                                                  'placeholder': 'yyyy-mm-dd'}))

        self.fields['export_to_date'] = forms.DateField(required=False,
                                                        widget=TextInput(attrs={'class': 'datepicker',
                                                                                'placeholder': 'yyyy-mm-dd'}))


class DataWarehouseUpdateForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['update_warehouse_date'] = forms.DateField(required=False, label='Update from',
                                                               widget=TextInput(attrs={'class': 'datepicker',
                                                                                       'placeholder': 'yyyy-mm-dd'}))


class UpdateDayDataForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['from_date'] = forms.DateField(required=True, widget=TextInput(attrs={'class': 'datepicker',
                                                                                          'placeholder': 'yyyy-mm-dd'}))

        self.fields['to_date'] = forms.DateField(required=True, widget=TextInput(attrs={'class': 'datepicker',
                                                                                        'placeholder': 'yyyy-mm-dd'}))


class UpdateTSBForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        table_choices = [(t, t) for t in DataWarehouse.instance().tables()]

        self.fields['table_choice'] = forms.CharField(required=False, label='Column:',
                                               widget=SelectMultiple(choices=table_choices,
                                                                     attrs={'class': 'form-control', 'id': 'table_choice',
                                                                            'multiple': 'multiple'}))

        self.fields['from_date'] = forms.DateField(required=True, widget=TextInput(attrs={'class': 'datepicker',
                                                                                          'placeholder': 'yyyy-mm-dd'}))

        self.fields['to_date'] = forms.DateField(required=True, widget=TextInput(attrs={'class': 'datepicker',
                                                                                        'placeholder': 'yyyy-mm-dd'}))


class UpdateInterpolationForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        col_choices = [(c,c) for c in WarehouseColumn.interpolated_columns()]

        self.fields['col_choice'] = forms.CharField(required=True, label='Column:',
                                                    widget=Select(choices=col_choices,
                                                                  attrs={'class': 'form-control', 'id': 'col_choice'}))

        self.fields['from_date'] = forms.DateField(required=True, widget=TextInput(attrs={'class': 'datepicker',
                                                                                          'placeholder': 'yyyy-mm-dd'}))

        self.fields['to_date'] = forms.DateField(required=True, widget=TextInput(attrs={'class': 'datepicker',
                                                                                        'placeholder': 'yyyy-mm-dd'}))

class UpdateHRVForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['from_date'] = forms.DateField(required=True, widget=TextInput(attrs={'class': 'datepicker',
                                                                                          'placeholder': 'yyyy-mm-dd'}))

        self.fields['to_date'] = forms.DateField(required=True, widget=TextInput(attrs={'class': 'datepicker',
                                                                                        'placeholder': 'yyyy-mm-dd'}))
