from django import template
import datetime
import decimal


register = template.Library()

# these are used in templates to format the html output

@register.filter
def duration(td):
    if td is None:
        return "00:00:00"
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    return '{} hours {} min'.format(hours, minutes)


@register.filter
def summary_filter(td):
    if td is None:
        return ""

    if isinstance(td, datetime.timedelta):
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return '{:,}:{:02d}'.format(hours, minutes)

    elif isinstance(td, decimal.Decimal):
        return '{:,}'.format(round(td))

    elif isinstance(td, int):
        return '{:,}'.format(td)

    return td
