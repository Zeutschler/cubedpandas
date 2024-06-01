from enum import IntEnum


class CachingStrategy(IntEnum):
    """
    Caching strategy for cubes. Used to determine if, when and how data should be cached.
    """
    NONE = 0
    LAZY = 1
    EAGER = 2
    FULL = 3

    def __str__(self):
        match self.value:
            case 0:
                return 'NONE - no caching'
            case 1:
                return 'LAZY - caching on first access'
            case 2:
                return 'EAGER - pre caching of low cardinality dimensions, other on access'
            case 3:
                return 'FULL - pre caching of all dimensions. Not recommended for large high cardinality datasets'
            case _:
                return 'UNKNOWN'
