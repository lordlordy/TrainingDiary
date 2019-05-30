

SUFFIXES = {1: 'st', 2: 'nd', 3: 'rd'}
def ordinal(number):
    suffix = SUFFIXES.get(number % 10, 'th')
    if 10 <= number % 10 <= 20:
        suffix = 'th'

    return str(number) + suffix