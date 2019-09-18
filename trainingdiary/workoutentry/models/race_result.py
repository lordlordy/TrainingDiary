


class RaceResult:

    def __init__(self, *args):
        self.primary_key = args[0]
        self.date = args[1]
        self.race_number = args[2]
        self.type = args[3]
        self.brand = args[4]
        self.distance = args[5]
        self.name = args[6]
        self.category = args[7]
        self.overall_position = args[8]
        self.category_position = args[9]
        self.swim_seconds = args[10]
        self.t1_seconds = args[11]
        self.bike_seconds = args[12]
        self.t2_seconds = args[13]
        self.run_seconds = args[14]
        self.swim_km = args[15]
        self.bike_km = args[16]
        self.run_km = args[17]
        self.comments = args[18]
        self.race_report = args[19]
        self.last_sav = args[20]
        self.total_seconds = self.swim_seconds + self.t1_seconds + self.bike_seconds + self.t2_seconds + self.run_seconds
        self.total_km = self.swim_km + self.bike_km + self.run_km

