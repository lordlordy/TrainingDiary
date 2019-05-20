from workoutentry.models import Day
import django_filters
from django.forms.widgets import TextInput, SelectMultiple, NumberInput

# this is to avoid a side effect of building db from scratch. Since these class variables query the DB they fail
# if DB not there when this is loaded. So instead do this:
from django.db.utils import OperationalError
sleep_quality_choices = [('Good','Good'), ('Average', 'Average'), ('Poor', 'Poor')]
type_choices = [('Normal', 'Normal'), ('Travel', 'Travel')]
try:
    sleep_quality_choices = [(a['sleep_quality'], a['sleep_quality']) for a in Day.objects.values('sleep_quality').distinct()]
    type_choices = [(a['type'], a['type']) for a in Day.objects.values('type').distinct()]
except OperationalError:
    pass


class DayFilter(django_filters.FilterSet):
    start_date_lte = django_filters.DateFilter(field_name='date', lookup_expr='lte', label='',
                                          widget=TextInput(attrs={'class': 'datepicker',
                                                                  'placeholder': 'to: yyyy-mm-dd'}))
    start_date_gte = django_filters.DateFilter(field_name='date', lookup_expr='gte', label='',
                                          widget=TextInput(attrs={'class': 'datepicker',
                                                                  'placeholder': 'from: yyyy-mm-dd'}))
    sleep_lte = django_filters.NumberFilter(field_name='sleep', lookup_expr='lte', label='')
    sleep_gte = django_filters.NumberFilter(field_name='sleep', lookup_expr='gte', label='')
    fatigue_lte = django_filters.NumberFilter(field_name='fatigue', lookup_expr='lte', label='')
    fatigue_gte = django_filters.NumberFilter(field_name='fatigue', lookup_expr='gte', label='')
    motivation_lte = django_filters.NumberFilter(field_name='motivation', lookup_expr='lte', label='')
    motivation_gte = django_filters.NumberFilter(field_name='motivation', lookup_expr='gte', label='')
    sleep_quality = django_filters.MultipleChoiceFilter(field_name='sleep_quality', label='',
                                                        choices=sleep_quality_choices,
                                                        widget=SelectMultiple(
                                                            attrs={'class': 'form-control', 'id': 'sleep_quality',
                                                                   'multiple': 'multiple'}))
    type = django_filters.MultipleChoiceFilter(field_name='type', label='',choices=type_choices,
                                               widget=SelectMultiple(attrs={'class': 'form-control', 'id': 'type',
                                                                            'multiple': 'multiple'}))
    comments = django_filters.CharFilter(lookup_expr='icontains', label='')

    class Meta:
        model = Day
        fields = ['date']

