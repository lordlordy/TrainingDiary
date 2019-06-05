from workoutentry.models import KG, FatPercentage, RestingHeartRate, SDNN, RMSSD
import django_filters
from django.forms.widgets import TextInput


class PhysiologicalFilter(django_filters.FilterSet):
    date_lte = django_filters.DateFilter(field_name='date', lookup_expr='lte', label='',
                                          widget=TextInput(attrs={'class': 'datepicker',
                                                                  'placeholder': 'to: yyyy-mm-dd'}))
    date_gte = django_filters.DateFilter(field_name='date', lookup_expr='gte', label='',
                                          widget=TextInput(attrs={'class': 'datepicker',
                                                                  'placeholder': 'from: yyyy-mm-dd'}))
    value_lte = django_filters.NumberFilter(field_name='value', lookup_expr='lte', label='')
    value_gte = django_filters.NumberFilter(field_name='value', lookup_expr='gte', label='')


class KGFilter(PhysiologicalFilter):
    class Meta:
        model = KG
        fields = ['date']


class FatPercentageFilter(PhysiologicalFilter):
    class Meta:
        model = FatPercentage
        fields = ['date']


class RestingHRFilter(PhysiologicalFilter):
    class Meta:
        model = RestingHeartRate
        fields = ['date']


class SDNNFilter(PhysiologicalFilter):
    class Meta:
        model = SDNN
        fields = ['date']


class RMSSDFilter(PhysiologicalFilter):
    class Meta:
        model = RMSSD
        fields = ['date']
