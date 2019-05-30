class WorkoutEntryRouter(object):
    """
    A router to control all database operations on models in the
    workoutentry application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read workoutentry models go to training_diary_db.
        """
        if model._meta.app_label == 'workoutentry':
            return 'training_diary_db'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write workoutentry models go to training_diary_db.
        """
        if model._meta.app_label == 'workoutentry':
            return 'training_diary_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the workoutentry app is involved.
        """
        if obj1._meta.app_label == 'workoutentry' and \
           obj2._meta.app_label == 'workoutentry':
           return True
        elif 'workoutentry' not in [obj1._meta.app_label, obj2._meta.app_label]:
            return None

        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the workoutentry app only appears in the 'training_diary_db'
        database.
        """
        if app_label == 'workoutentry':
            return db == 'training_diary_db'
        elif db == 'training_diary_db':
            return False

        return None
