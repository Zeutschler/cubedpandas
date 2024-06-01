from enum import IntEnum

EAGER_CACHING_THRESHOLD: int = 256  # upper dimension cardinality limit (# of members in dimension) for EAGER caching

class CachingStrategy(IntEnum):
    """
    Caching strategy for faster data access to cubes. Defines if, when and how data should be cached.

    Recommended value for most use cases is `LAZY` caching (caching on first access). For smaller datasets or datasets
    with low cardinality dimensions, `EAGER` caching (pre caching of low cardinality dimensions, other on access) can
    be beneficial.

    `FULL` caching (pre caching of all dimensions) is recommended only for long-living and smaller, low cardinality
    datasets where fast access is crucial, e.g. using CubedPandas for data access through a web service.
    `FULL` caching should be avoided for large or short-living datasets due to the implied memory and run-time penalty.
    `NONE` caching is recommended for large datasets, when memory is limited, when the dataset is not used frequently
    or when the performance is not crucial.
    """
    NONE = 0
    LAZY = 1
    EAGER = 2
    FULL = 3

    def __str__(self):
        match self.value:
            case 0:
                return 'NONE'  # - no caching'
            case 1:
                return 'LAZY'  # - caching on first access'
            case 2:
                return 'EAGER'  # - pre caching of low cardinality dimensions, other on access'
            case 3:
                return 'FULL'  # - pre caching of all dimensions. Not recommended for large high cardinality datasets'
            case _:
                return 'UNKNOWN'
