from enum import Enum


class DayAggregation(Enum):
    SUM = "Sum"
    MEAN = "Mean"
    MAX = "Max"
    MIN = "Min"
    TIME_WEIGHTED_AVERAGE = "Time Weighted Average"
    DISTANCE_WEIGHTED_AVERAGE = "Distance Weight Average"


class Aggregation(Enum):
    SUM = 'Sum'
    MEAN = 'Mean'
    MAX = 'Max'
    MEDIAN = 'Median'
    MIN = 'Min'
    STD_DEV = 'Std_Dev'


class PandasInterpolation(Enum):
    NONE = 'none'
    FILL_ZERO = 'fill zero'
    LINEAR = 'linear'
    TIME = 'time'
    NEAREST = 'nearest'
    ZERO = 'zero'
    SLINEAR = 'slinear'
    QUADRATIC = 'quadratic'
    CUBIC = 'cubic'
    SPLINE = 'spline'
    BARYCENTRIC = 'barycentric'
    POLYNOMIAL = 'polynomial'
    KROGH = 'krogh'
    PIECEWISE_POLYNOMIAL = 'piecewise_polynomial'
    PCHIP = 'pchip'
    AKIMA = 'akima'
    CUBIC_SPLINE = 'cubicspline'


class PandasPeriod(Enum):
    DAY = 'Day'
    W_MON = 'W-Mon'
    W_TUE = 'W-Tue'
    W_WED = 'W-Wed'
    W_THU = 'W-Thu'
    W_FRI = 'W-Fri'
    W_SAT = 'W-Sat'
    W_SUN = 'W-Sun'
    MONTH = 'M'
    Y_JAN = 'A-Jan'
    Y_FEB = 'A-Feb'
    Y_MAR = 'A-Mar'
    Y_APR = 'A-Apr'
    Y_MAY = 'A-May'
    Y_JUN = 'A-Jun'
    Y_JUL = 'A-Jul'
    Y_AUG = 'A-Aug'
    Y_SEP = 'A-Sep'
    Y_OCT = 'A-Oct'
    Y_NOV = 'A-Nov'
    Y_DEC = 'A-Dec'
    Q_JAN = 'Q-Jan'
    Q_FEB = 'Q-Feb'
    Q_MAR = 'Q-Mar'


class WorkoutFloatMeasureEnum(Enum):
    SECONDS = 'seconds'
    MINUTES = 'minutes'
    HOURS = 'hours'
    RPE = 'rpe'
    TSS = 'tss'
    KM = 'km'
    MILES = 'miles'
    KJ = 'kj'
    ASCENT_METRES = 'ascent_metres'
    ASCENT_FEET = 'ascent_feet'
    REPS = 'reps'
    CADENCE = 'cadence'
    WATTS = 'watts'
    HEART_RATE = 'heart_rate'


class ReadingEnum(Enum):
    KG = 'kg'
    LBS = 'lbs'
    FAT_PERCENTAGE = 'fatPercentage'
    RESTING_HEART_RATE = 'restingHR'
    FATIGUE = 'fatigue'
    MOTIVATION = 'motivation'

