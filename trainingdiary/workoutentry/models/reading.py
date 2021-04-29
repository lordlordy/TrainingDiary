import dateutil.parser


class Reading:

    def __init__(self, *args):
        self.date = dateutil.parser.parse(args[0]).date()
        self.date_str = args[0]
        self.reading_type = args[1]
        self.value = args[2]
        self.primary_key = args[3]

    def __str__(self):
        return self.date_str + " ~ " + self.reading_type + ":" + str(self.value)

    def data_dictionary(self):
        return {'primary_key': self.primary_key,
                'DT_RowId': self.primary_key,
                'date': self.date_str,
                'reading_type': self.reading_type,
                'value': self.value}

    def json_dictionary(self):
        return {'type': self.reading_type, 'value': self.value}