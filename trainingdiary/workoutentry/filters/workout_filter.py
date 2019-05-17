from workoutentry.models import Workout
import django_filters
from django.forms.widgets import TextInput
from django.forms.widgets import SelectMultiple

# this is to avoid a side effect of building db from scratch. Since these class variables query the DB they fail
# if DB not there when this is loaded. So instead do this:
from django.db.utils import OperationalError
activity_choices = [('Run','Run'), ('Bike', 'Bike'), ('Swim', 'Swim')]
activity_type_choices = [('Road', 'Road'), ('Squad', 'Squad')]
tss_method_choices = [('RPE', 'RPE'), ('PacePower', 'PacePower')]
equipment_choices = [('IF XS', 'IF XS'), ('Roberts', 'Roberts')]
try:
    activity_choices = [(a['activity'], a['activity']) for a in Workout.objects.values('activity').distinct()]
    activity_type_choices = [(a['activity_type'], a['activity_type']) for a in Workout.objects.values('activity_type').distinct()]
    tss_method_choices = [(a['tss_method'], a['tss_method']) for a in Workout.objects.values('tss_method').distinct()]
    equipment_choices = [(a['equipment'], a['equipment']) for a in Workout.objects.values('equipment').distinct()]
except OperationalError:
    pass


class WorkoutFilter(django_filters.FilterSet):
    date_lte = django_filters.DateFilter(field_name='day__date', lookup_expr='lte', label='date (<=)',
                                         widget=TextInput(attrs={'class': 'datepicker',
                                                                 'placeholder': 'yyyy-mm-dd'}))
    date_gte = django_filters.DateFilter(field_name='day__date', lookup_expr='gte',  label='date (>=)',
                                         widget=TextInput(attrs={'class': 'datepicker',
                                                                 'placeholder': 'yyyy-mm-dd'}))
    km_gte = django_filters.NumberFilter(field_name='km', lookup_expr='gte', label='km (>=)')
    km_lte = django_filters.NumberFilter(field_name='km', lookup_expr='lte', label='km (<=)')
    kj_gte = django_filters.NumberFilter(field_name='kj', lookup_expr='gte', label='kj (>=)')
    kj_lte = django_filters.NumberFilter(field_name='kj', lookup_expr='lte', label='kj (<=)')
    rpe_gte = django_filters.NumberFilter(field_name='rpe', lookup_expr='gte', label='rpe (>=)')
    rpe_lte = django_filters.NumberFilter(field_name='rpe', lookup_expr='lte', label='rpe (<=)')
    tss_gte = django_filters.NumberFilter(field_name='tss', lookup_expr='gte', label='tss (>=)')
    tss_lte = django_filters.NumberFilter(field_name='tss', lookup_expr='lte', label='tss (<=)')
    ascent_gte = django_filters.NumberFilter(field_name='ascent_metres', lookup_expr='gte', label='ascent (>=)')
    ascent_lte = django_filters.NumberFilter(field_name='ascent_metres', lookup_expr='lte', label='ascent (<=)')
    cadence_gte = django_filters.NumberFilter(field_name='cadence', lookup_expr='gte', label='cadence (>=)')
    cadence_lte = django_filters.NumberFilter(field_name='cadence', lookup_expr='lte', label='cadence (<=)')
    watts_gte = django_filters.NumberFilter(field_name='watts', lookup_expr='gte', label='watts (>=)')
    watts_lte = django_filters.NumberFilter(field_name='watts', lookup_expr='lte', label='watts (<=)')
    hr_gte = django_filters.NumberFilter(field_name='heart_rate', lookup_expr='gte', label='hr (>=)')
    hr_lte = django_filters.NumberFilter(field_name='heart_rate', lookup_expr='lte', label='hr (<=)')
    reps_gte = django_filters.NumberFilter(field_name='reps', lookup_expr='gte', label='reps (>=)')
    reps_lte = django_filters.NumberFilter(field_name='reps', lookup_expr='lte', label='reps (<=)')
    duration_gte = django_filters.DurationFilter(field_name='duration', lookup_expr='gte', label='duration (>=)')
    duration_lte = django_filters.DurationFilter(field_name='duration', lookup_expr='lte', label='duration (<=)')
    activity = django_filters.MultipleChoiceFilter(label='Activity', field_name='activity',
                                                   choices=activity_choices,
                                                   widget=SelectMultiple(attrs={'class': 'form-control', 'id': 'activity', 'multiple': 'multiple'}))
    activity_type = django_filters.MultipleChoiceFilter(label='Activity Type', field_name='activity_type',
                                                        choices=activity_type_choices,
                                                        widget=SelectMultiple(attrs={'class': 'form-control', 'id': 'activity_type', 'multiple': 'multiple'}))
    tss_method = django_filters.MultipleChoiceFilter(label='TSS Method', field_name='tss_method',
                                                     choices=tss_method_choices,
                                                     widget=SelectMultiple(attrs={'class': 'form-control', 'id': 'tss_method', 'multiple': 'multiple'}))
    equipment = django_filters.MultipleChoiceFilter(label='Equipment', field_name='equipment',
                                                     choices=equipment_choices,
                                                     widget=SelectMultiple(
                                                         attrs={'class': 'form-control', 'id': 'equipment',
                                                                'multiple': 'multiple'}))
    comments = django_filters.CharFilter(lookup_expr='icontains', label='Comments')
    keywords = django_filters.CharFilter(lookup_expr='icontains', label='Keywords')
    is_race = django_filters.BooleanFilter(label='Race?')
    watts_estimated = django_filters.BooleanFilter(label='Watts Est?')
    is_brick = django_filters.BooleanFilter(label='Brick?')

    class Meta:
        model = Workout
        fields = ['km']
