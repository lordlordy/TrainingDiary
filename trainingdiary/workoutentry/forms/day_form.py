# from django import forms
# from django.forms.widgets import TextInput
# from django.forms.widgets import Select
# from workoutentry.training_data import TrainingDataManager
#
#
# class DayFilterForm(forms.Form):
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#
#         self.fields['from'] = forms.DateField(required=False, widget=TextInput(attrs={'class': 'datepicker',
#                                                                                     'placeholder': 'yyyy-mm-dd'}))
#
#         self.fields['to'] = forms.DateField(required=False, widget=TextInput(attrs={'class': 'datepicker',
#                                                                                   'placeholder': 'yyyy-mm-dd'}))
#
#
# class DayEditForm(forms.Form):
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         self.fields['date'] = forms.CharField(widget=TextInput(attrs={'readonly': 'readonly'}))
#         unique_types = TrainingDataManager().day_types()
#         self.fields['day_type'] = forms.CharField(required=True,
#                                               widget=Select(choices=[(u, u) for u in unique_types],
#                                                             attrs={'class': 'form-control', 'id': 'type'}))
#
#         self.fields['comments'] = forms.CharField(required=False, widget=forms.Textarea())