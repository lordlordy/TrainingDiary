import dateutil.parser

class Reading:

    def __init__(self, *args):
        self.date = dateutil.parser.parse(args[0]).date()
        self.reading_type = args[1]
        self.value = args[2]

    def __str__(self):
        return self.date + " ~ " + self.reading_type + ":" + str(self.value)