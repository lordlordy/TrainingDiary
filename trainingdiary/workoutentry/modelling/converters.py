def measure_converter(measure):
    if measure == 'hours':
        return Converter('seconds', lambda x: x / 3600)
    elif measure == 'minutes':
        return Converter('seconds', lambda x: x / 60)
    elif measure == 'miles':
        return Converter('km', lambda x: x / 1.60934)
    elif measure == 'lbs':
        return Converter('kg', lambda x: x * 2.20462)
    return None


class Converter:

    def __init__(self, underlying_measure, convert_lambda):
        self.__underlying_measure = underlying_measure
        self.__convert_lambda = convert_lambda

    def underlying_measure(self):
        return self.__underlying_measure

    def convert_lambda(self):
        return self.__convert_lambda




