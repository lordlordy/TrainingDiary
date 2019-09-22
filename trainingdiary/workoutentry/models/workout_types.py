
class WorkoutType:

    __cache = {}

    @classmethod
    def workout_type_for(cls, activity=None, activity_type=None, equipment=None):
        name = WorkoutType.name_for(activity=activity, activity_type=activity_type, equipment=equipment)
        if name not in cls.__cache:
            cls.__cache[name] = WorkoutType(activity=activity, activity_type=activity_type, equipment=equipment)
        return cls.__cache[name]

    @classmethod
    def name_for(cls, activity=None, activity_type=None, equipment=None):
        a = "All" if activity is None else activity
        at = "All" if activity_type is None else activity_type
        e = "All" if equipment is None or equipment == "" else equipment
        return '_'.join([a,at,e])

    def __init__(self, activity=None, activity_type=None, equipment=None):
        self.activity = activity
        self.activity_type = activity_type
        self.equipment = equipment
        self.name = WorkoutType.name_for(activity=activity, activity_type=activity_type, equipment=equipment)

    def __str__(self):
        return self.name

