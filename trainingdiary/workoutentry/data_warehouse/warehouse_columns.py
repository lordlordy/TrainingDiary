

class WarehouseColumn:

    date = "date"
    year = "year"
    year_week = "year_week"
    year_for_week = "year_for_week_of_year"
    year_month = "year_month"
    year_quarter = "year_quarter"
    day_of_week = "day_of_week"
    month = "month"
    week = "week"
    quarter = "quarter"
    day_type = "day_type"
    fatigue = "fatigue"
    motivation = "motivation"
    sleep_seconds = "sleep_seconds"
    sleep_minutes = "sleep_minutes"
    sleep_hours = "sleep_hours"
    sleep_score = "sleep_score"
    sleep_quality = "sleep_quality"
    sleep_quality_score = "sleep_quality_score"
    km = "km"
    miles = "miles"
    tss = "tss"
    rpe = "rpe"
    hr = "hr"
    watts = "watts"
    seconds = "seconds"
    minutes = "minutes"
    hours = "hours"
    ascent_metres = "ascent_metres"
    ascent_feet = "ascent_feet"
    kj = "kj"
    reps = "reps"
    is_race = "is_race"
    brick = "brick"
    watts_estimated = "watts_estimated"
    cadence = "cadence"
    rpe_tss = "rpe_tss"
    mph = "mph"
    kph = "kph"
    ctl = "ctl"
    atl = "atl"
    tsb = "tsb"
    rpe_ctl = "rpe_ctl"
    rpe_atl = "rpe_atl"
    rpe_tsb = "rpe_tsb"
    monotony = "monotony"
    strain = "strain"
    rpe_monotony = "rpe_monotony"
    rpe_strain = "rpe_strain"
    kg = "kg"
    lbs = "lbs"
    fat_percentage = "fat_percentage"
    resting_hr = "resting_hr"
    sdnn = "sdnn"
    rmssd = "rmssd"
    kg_recorded = "kg_recorded"
    lbs_recorded = "lbs_recorded"
    fat_percentage_recorded = "fat_percentage_recorded"
    resting_hr_recorded = "resting_hr_recorded"
    sdnn_recorded = "sdnn_recorded"
    rmssd_recorded = "rmssd_recorded"
    sdnn_off = "sdnn_off"
    sdnn_easy = "sdnn_easy"
    sdnn_hard = "sdnn_hard"
    sdnn_mean = "sdnn_mean"
    sdnn_std_dev = "sdnn_std_dev"
    rmssd_off = "rmssd_off"
    rmssd_easy = "rmssd_easy"
    rmssd_hard = "rmssd_hard"
    rmssd_mean = "rmssd_mean"
    rmssd_std_dev = "rmssd_std_dev"

    @classmethod
    def all_cols(cls):
        return [cls.date, cls.year, cls.year_week, cls.year_for_week, cls.year_month, cls.year_quarter, cls.day_of_week,
                cls.month, cls.week, cls.quarter, cls.day_type, cls.fatigue, cls.motivation, cls.sleep_seconds,
                cls.sleep_minutes, cls.sleep_hours, cls.sleep_score, cls.sleep_quality, cls.sleep_quality_score, cls.km,
                cls.miles, cls.tss, cls.rpe, cls.hr, cls.watts, cls.seconds, cls.minutes, cls.hours, cls.ascent_metres,
                cls.ascent_feet, cls.kj, cls.reps, cls.is_race, cls.brick, cls.watts_estimated , cls.cadence,
                cls.rpe_tss, cls.mph, cls.kph, cls.ctl, cls.atl, cls.tsb, cls.rpe_ctl, cls.rpe_atl, cls.rpe_tsb,
                cls.monotony, cls.strain, cls.rpe_monotony, cls.rpe_strain, cls.kg, cls.lbs, cls.fat_percentage,
                cls.resting_hr, cls.sdnn, cls.rmssd, cls.kg_recorded, cls.lbs_recorded, cls.fat_percentage_recorded,
                cls.resting_hr_recorded, cls.sdnn_recorded, cls.rmssd_recorded, cls.sdnn_off, cls.sdnn_easy,
                cls.sdnn_hard, cls.sdnn_mean, cls.sdnn_std_dev, cls.rmssd_off, cls.rmssd_easy,
                cls.rmssd_hard, cls.rmssd_mean, cls.rmssd_std_dev]

    @classmethod
    def day_cols(cls):
        return [cls.date, cls.year, cls.year_week, cls.year_for_week, cls.year_month, cls.year_quarter, cls.day_of_week,
                cls.month, cls.week, cls.quarter, cls.day_type, cls.fatigue, cls.motivation, cls.sleep_seconds,
                cls.sleep_minutes, cls.sleep_hours, cls.sleep_score, cls.sleep_quality, cls.sleep_quality_score, cls.km,
                cls.miles, cls.tss, cls.rpe, cls.hr, cls.watts, cls.seconds, cls.minutes, cls.hours, cls.ascent_metres,
                cls.ascent_feet, cls.kj, cls.reps, cls.is_race, cls.brick, cls.watts_estimated , cls.cadence,
                cls.rpe_tss, cls.mph, cls.kph, cls.ctl, cls.atl, cls.tsb, cls.rpe_ctl, cls.rpe_atl, cls.rpe_tsb,
                cls.monotony, cls.strain, cls.rpe_monotony, cls.rpe_strain, cls.kg, cls.lbs, cls.fat_percentage,
                cls.resting_hr, cls.sdnn, cls.rmssd, cls.kg_recorded, cls.lbs_recorded, cls.fat_percentage_recorded,
                cls.resting_hr_recorded, cls.sdnn_recorded, cls.rmssd_recorded, cls.sdnn_off, cls.sdnn_easy,
                cls.sdnn_hard, cls.sdnn_mean, cls.sdnn_std_dev, cls.rmssd_off, cls.rmssd_easy, cls.rmssd_hard,
                cls.rmssd_mean, cls.rmssd_std_dev]

    @classmethod
    def interpolated_columns(cls):
        return [cls.kg, cls.lbs, cls.fat_percentage, cls.resting_hr, cls.sdnn, cls.rmssd]

    def __init__(self, name):
        self.name = name

    def sql_type_str(self):

        if self.name in {WarehouseColumn.date}:
            return "date PRIMARY KEY"
        elif self.name in {WarehouseColumn.month, WarehouseColumn.day_of_week}:
            return "varchar(8) NOT NULL"
        elif self.name in {WarehouseColumn.year, WarehouseColumn.year_week, WarehouseColumn.year_for_week,
                           WarehouseColumn.year_month, WarehouseColumn.day_type, WarehouseColumn.year_quarter,
                           WarehouseColumn.week, WarehouseColumn.quarter}:
            return "varchar(16) NOT NULL"
        elif self.name in {WarehouseColumn.sleep_quality}:
            return "varchar(16) NOT NULL DEFAULT 'Average'"
        elif self.name in {WarehouseColumn.fatigue, WarehouseColumn.motivation, WarehouseColumn.sleep_hours,
                           WarehouseColumn.km, WarehouseColumn.miles, WarehouseColumn.rpe, WarehouseColumn.hours,
                           WarehouseColumn.mph, WarehouseColumn.kph, WarehouseColumn.ctl, WarehouseColumn.atl,
                           WarehouseColumn.tsb, WarehouseColumn.rpe_ctl, WarehouseColumn.rpe_atl,
                           WarehouseColumn.rpe_tsb, WarehouseColumn.monotony, WarehouseColumn.strain,
                           WarehouseColumn.rpe_monotony, WarehouseColumn.rpe_strain, WarehouseColumn.kg,
                           WarehouseColumn.lbs, WarehouseColumn.fat_percentage, WarehouseColumn.sdnn,
                           WarehouseColumn.rmssd, WarehouseColumn.sleep_quality_score, WarehouseColumn.sleep_score,
                           WarehouseColumn.sdnn_off, WarehouseColumn.sdnn_easy, WarehouseColumn.sdnn_hard,
                           WarehouseColumn.sdnn_mean, WarehouseColumn.sdnn_std_dev, WarehouseColumn.rmssd_off,
                           WarehouseColumn.rmssd_easy, WarehouseColumn.rmssd_hard, WarehouseColumn.rmssd_mean,
                           WarehouseColumn.rmssd_std_dev}:
            return "REAL DEFAULT 0.0 NOT NULL"
        elif self.name in {WarehouseColumn.sleep_minutes, WarehouseColumn.sleep_seconds, WarehouseColumn.tss,
                           WarehouseColumn.rpe_tss, WarehouseColumn.hr, WarehouseColumn.watts, WarehouseColumn.seconds,
                           WarehouseColumn.minutes, WarehouseColumn.ascent_feet, WarehouseColumn.ascent_metres,
                           WarehouseColumn.kj, WarehouseColumn.reps, WarehouseColumn.cadence,
                           WarehouseColumn.resting_hr}:
            return "INTEGER DEFAULT 0 NOT NULL"
        elif self.name in {WarehouseColumn.is_race, WarehouseColumn.brick, WarehouseColumn.watts_estimated,
                           WarehouseColumn.kg_recorded, WarehouseColumn.lbs_recorded,
                           WarehouseColumn.fat_percentage_recorded, WarehouseColumn.resting_hr_recorded,
                           WarehouseColumn.sdnn_recorded, WarehouseColumn.rmssd_recorded}:
            return "BOOLEAN DEFAULT 0 NOT NULL"

    def recorded_column_name(self):
        if self.name in WarehouseColumn.interpolated_columns():
            return f"{self.name}_recorded"
        else:
            return None

    def sql_str(self):
        return f'{self.name} {self.sql_type_str()}'