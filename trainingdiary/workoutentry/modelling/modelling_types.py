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


class PandasPeriod(Enum):
    DAY = 'Day'
    W_MON = 'W-Mon'
    W_TUE = 'W-Tue'
    W_WED = 'W-Wed'
    W_THU = 'W-Thu'
    W_FRI = 'W-Fri'
    W_SAT = 'W-Sat'
    W_SUN = 'W-Sun'
    MONTH = 'Month'
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