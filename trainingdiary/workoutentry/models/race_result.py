from datetime import timedelta
import dateutil

class RaceResult:

    def __init__(self, *args):
        self.primary_key = args[0]
        self.date_str = args[1]
        self.date = dateutil.parser.parse(args[1]).date()
        self.year = self.date.year
        self.race_number = args[2]
        self.type = args[3]
        self.brand = args[4]
        self.distance = args[5]
        self.name = args[6]
        self.category = args[7]
        self.overall_position = args[8]
        self.category_position = args[9]
        self.__swimSeconds = args[10]
        self.swim_seconds = timedelta(seconds=args[10])
        self.__t1Seconds = args[11]
        self.t1_seconds = timedelta(seconds=args[11])
        self.__bikeSeconds = args[12]
        self.bike_seconds = timedelta(seconds=args[12])
        self.__t2Secconds = args[13]
        self.t2_seconds = timedelta(seconds=args[13])
        self.__runSeconds = args[14]
        self.run_seconds = timedelta(seconds=args[14])
        self.swim_km = args[15]
        self.bike_km = args[16]
        self.run_km = args[17]
        self.comments = args[18]
        self.race_report = args[19]
        self.last_save = args[20]
        self.total_seconds = self.swim_seconds + self.t1_seconds + self.bike_seconds + self.t2_seconds + self.run_seconds
        self.total_km = self.swim_km + self.bike_km + self.run_km

    def data_dictionary(self):
        return {'primary_key': self.primary_key,
                'date': self.date_str,
                'year': self.year,
                'race_number': self.race_number,
                'type': self.type,
                'brand': self.brand,
                'distance': self.distance,
                'name': self.name,
                'category': self.category,
                'overall_position': self.overall_position,
                'category_position': self.category_position,
                'swim_seconds': self.swim_seconds,
                't1_seconds': self.t1_seconds,
                'bike_seconds': self.bike_seconds,
                't2_seconds': self.t2_seconds,
                'run_seconds': self.run_seconds,
                'swim_km': self.swim_km,
                'bike_km': self.bike_km,
                'run_km': self.run_km,
                'comments': self.comments,
                'race_report': self.race_report,
                'last_save': self.last_save,
                'total_seconds': self.total_seconds,
                'total_km': self.total_km}

    def json_dictionary(self):
        return {"t1Seconds": self.__t1Seconds,
                "categoryPosition": self.category_position,
                "bikeSeconds": self.__bikeSeconds,
                "swimSeconds": self.__swimSeconds,
                "comments": self.comments,
                "swimKM": self.swim_km,
                "distance": self.distance,
                "t2Seconds": self.__t2Secconds,
                "name": self.name,
                "type": self.type,
                "runKM": self.run_km,
                "overallPosition": self.overall_position,
                "bikeKM": self.bike_km,
                "raceReport": self.race_report,
                "iso8601DateString": self.date_str,
                "brand": self.brand,
                "raceNumber": self.race_number,
                "runSeconds": self.__runSeconds,
                "category": self.category}