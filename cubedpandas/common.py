from enum import IntEnum

class CubeAggregationFunctionType(IntEnum):
    """Aggregation functions supported for the value in a cube.
    """
    SUM = 1
    AVG = 2
    MEDIAN = 3
    MIN = 4
    MAX = 5
    COUNT = 6
    STDDEV = 7
    VAR = 8
    POF = 9
    NAN = 10
    AN = 11

