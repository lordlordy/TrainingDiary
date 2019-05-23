from .eddington_number_form import EddingtonNumberForm
from workoutentry.data_warehouse import Graph
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from django import forms
from django.forms.widgets import Select, TextInput


class GraphForm(EddingtonNumberForm):
    colour_map = dict([(i, m) for i, m in enumerate([m for m in plt.cm.datad if not m.endswith("_r")])])
    named_colours = dict([(i, m) for i, m in enumerate(mcolors.CSS4_COLORS)])
    SINGLE = 'Single'
    SPLIT = 'Split'
    TYPES = [SINGLE, SPLIT]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['colour_map'] = forms.CharField(required=True,
                                                  widget=Select(
                                                      choices=[(i, m) for i, m in GraphForm.colour_map.items()],
                                                      attrs={'class': 'form-control', 'id': 'colour_map'}))

        self.fields['graphs'] = forms.CharField(required=True,
                                                  widget=Select(
                                                      choices=[(i, i) for i in GraphForm.TYPES],
                                                      attrs={'class': 'form-control', 'id': 'graphs'}))


        self.fields['axis'] = forms.CharField(required=True,
                                                  widget=Select(
                                                      choices=[(i, i) for i in Graph.GRAPH_AXES],
                                                      attrs={'class': 'form-control', 'id': 'axis'}))

        self.fields['graph_type'] = forms.CharField(required=True,
                                                    widget=Select(
                                                      choices=[(i, i) for i in Graph.GRAPH_TYPES],
                                                      attrs={'class': 'form-control', 'id': 'graph_type'}))

        self.fields['size'] = forms.IntegerField(required=True, initial=3, min_value=1)

        self.fields['background'] =  forms.CharField(required=False,
                                                    widget=Select(
                                                      choices=[(i, i) for i in mcolors.CSS4_COLORS],
                                                      attrs={'class': 'form-control', 'id': 'background'}))

        self.fields['from'] = forms.DateField(required=False, widget=TextInput(attrs={'class': 'datepicker',
                                                                                    'placeholder': 'from: yyyy-mm-dd'}))

        self.fields['to'] = forms.DateField(required=False, widget=TextInput(attrs={'class': 'datepicker',
                                                                                  'placeholder': 'from: yyyy-mm-dd'}))

