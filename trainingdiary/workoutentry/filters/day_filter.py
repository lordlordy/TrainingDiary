from workoutentry.models import Day
import django_filters
from django.forms.widgets import TextInput



class DayFilter(django_filters.FilterSet):
    start_date_lte = django_filters.DateFilter(field_name='date', lookup_expr='lte',
                                          widget=TextInput(attrs={'class': 'datepicker',
                                                                  'placeholder': 'yyyy-mm-dd'}))
    start_date_gte = django_filters.DateFilter(field_name='date', lookup_expr='gte',
                                          widget=TextInput(attrs={'class': 'datepicker',
                                                                  'placeholder': 'yyyy-mm-dd'}))
    sleep_lte = django_filters.NumberFilter(field_name='sleep', lookup_expr='lte')
    sleep_gte = django_filters.NumberFilter(field_name='sleep', lookup_expr='gte')
    fatigue_lte = django_filters.NumberFilter(field_name='fatigue', lookup_expr='lte')
    fatigue_gte = django_filters.NumberFilter(field_name='fatigue', lookup_expr='gte')
    motivation_lte = django_filters.NumberFilter(field_name='motivation', lookup_expr='lte')
    motivation_gte = django_filters.NumberFilter(field_name='motivation', lookup_expr='gte')
    sleep_quality = django_filters.CharFilter(lookup_expr='icontains')
    type = django_filters.CharFilter(lookup_expr='icontains')
    comments = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Day
        fields = ['date']

