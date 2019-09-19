
class WorkoutType:

    def __init__(self, activity=None, activity_type=None, equipment=None):
        self.activity = activity
        self.activity_type = activity_type
        self.equipment = equipment

    def __str__(self):
        a = "All" if self.activity is None else self.activity
        at = "All" if self.activity_type is None else self.activity_type
        e = "All" if self.equipment is None or self.equipment == "" else self.equipment

        return ':'.join([a,at,e])
