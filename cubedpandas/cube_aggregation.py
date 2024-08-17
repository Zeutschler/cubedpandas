# CubedPandas - Copyright (c)2024 by Thomas Zeutschler, BSD 3-clause license, see LICENSE file.

from enum import IntEnum
from typing import SupportsFloat

import numpy as np


class CubeAllocationFunctionType(IntEnum):
    """
    Allocation functions supported for value write back in a cube.
    """
    DISTRIBUTE = 1
    """Distributes a new value to all affected records based on the current distribution of values."""
    SET = 2
    """Sets the new value to all affected records, independent of the current values."""
    DELTA = 3
    """Adds the new value to all affected records. Nan values are treated as zero values."""
    MULTIPLY = 4
    """Multiplies all affected records with the new value."""
    ZERO = 5
    """Sets all affected values/records to zero. Dependent on the measure type, the value is set to either (int) 0 or (float) 0.0."""
    NAN = 6
    """Sets all affected values/records to NaN."""
    DEL = 7
    """Deletes all affected records from the Pandas dataframe."""


class CubeAggregationFunctionType(IntEnum):
    """
    Aggregation functions supported by a cube.
    """
    # returning the dtype of the current measure or float
    SUM = 1
    """Sum of all values in the current context."""
    AVG = 2
    """Average of all values in the current context."""
    MEDIAN = 3
    """Median of all values/rows in the current context."""
    MIN = 4
    """Minimum of all values/rows in the current context."""
    MAX = 5
    """Maximum of all values/rows in the current context."""
    STD = 6
    """Standard deviation of all values/rows in the current context."""
    VAR = 7
    """Variance of all values/rows in the current context."""
    POF = 8
    """Percentage of the first value in the current context."""

    # returning an integer
    COUNT = 9
    """Number of values/rows in the current context."""
    NAN = 10
    """Number of NaN values/rows in the current context."""
    AN = 11
    """Number of non-NaN values/rows in the current context."""
    ZERO = 12
    """Number of zero values/rows in the current context."""
    NZERO = 13
    """Number of non-zero values/rows in the current context."""

    @staticmethod
    def is_count_function(function_type: int) -> bool:
        """Returns True if the function type represents one of the
        counting function types `COUNT`, `NAN`, `AN`, `ZERO` or `NZERO`."""
        return function_type >= CubeAggregationFunctionType.COUNT


class CubeAggregationFunction(SupportsFloat):
    """
    Represents aggregation functions, like SUM, MIN, MAX, VAG etc.,
    which are provided through the 'Cube' and 'Cell' object, e.g. by `cube.avg["Apple", "Online"]`.
    """

    def __new__(cls, *args, **kwargs):
        return SupportsFloat.__new__(cls)

    def __init__(self, cube, operation: CubeAggregationFunctionType = CubeAggregationFunctionType.SUM,
                 row_mask: np.ndarray | None = None, measure: str | None = None):
        self._cube = cube
        self._op: CubeAggregationFunctionType = operation
        self._row_mask: np.ndarray | None = row_mask
        self._measure: str | None = measure

    def __getitem__(self, address):
        row_mask, measure = self._cube._resolve_address(address, self._row_mask, self._measure)
        return self._cube._evaluate(row_mask, measure, self._op)

    def __setitem__(self, address, value):
        raise NotImplementedError("Not implemented yet")

    # region Properties
    @property
    def value(self):
        """Reads the value of the current cell idx_address from the underlying cube."""
        # if self._row_mask is None:
        #    return self._cube[None]
        return self._cube._evaluate(self._row_mask, self._measure, self._op)

    @value.setter
    def value(self, value):
        """Writes a value of the current cell idx_address to the underlying cube."""
        raise NotImplementedError("Not implemented yet")

    @property
    def numeric_value(self) -> float:
        """Reads the numeric value of the current cell idx_address from the underlying cube."""
        value = self.value
        if isinstance(value, (int, float, np.integer, np.floating, bool)):
            return float(value)
        else:
            return 0.0

    # region operator overloading and float behaviour
    def __float__(self) -> float:  # type conversion to float
        return self.numeric_value

    def __index__(self) -> int:  # type conversion to int
        return int(self.numeric_value)

    def __neg__(self):  # - unary operator
        return - self.numeric_value

    def __pos__(self):  # + unary operator
        return self.numeric_value

    def __add__(self, other):  # + operator
        return self.numeric_value + other

    def __iadd__(self, other):  # += operator
        return self.numeric_value + other.numeric_value

    def __radd__(self, other):  # + operator
        return other + self.numeric_value

    def __sub__(self, other):  # - operator
        return self.numeric_value - other

    def __isub__(self, other):  # -= operator
        return self.numeric_value - other

    def __rsub__(self, other):  # - operator
        return other - self.numeric_value

    def __mul__(self, other):  # * operator
        return self.numeric_value * other

    def __imul__(self, other):  # *= operator
        return self.numeric_value * other

    def __rmul__(self, other):  # * operator
        return self.numeric_value * other

    def __floordiv__(self, other):  # // operator (returns an integer)
        return self.numeric_value // other

    def __ifloordiv__(self, other):  # //= operator (returns an integer)
        return self.numeric_value // other

    def __rfloordiv__(self, other):  # // operator (returns an integer)
        return other // self.numeric_value

    def __truediv__(self, other):  # / operator (returns a float)
        return self.numeric_value / other

    def __idiv__(self, other):  # /= operator (returns a float)
        return self.numeric_value / other

    def __rtruediv__(self, other):  # / operator (returns a float)
        return other / self.numeric_value

    def __mod__(self, other):  # % operator (returns a tuple)
        return self.numeric_value % other

    def __imod__(self, other):  # %= operator (returns a tuple)
        return self.numeric_value % other

    def __rmod__(self, other):  # % operator (returns a tuple)
        return other % self.numeric_value

    def __divmod__(self, other):  # div operator (returns a tuple)
        return divmod(self.numeric_value, other)

    def __rdivmod__(self, other):  # div operator (returns a tuple)
        return divmod(other, self.numeric_value)

    def __pow__(self, other, modulo=None):  # ** operator
        return self.numeric_value ** other

    def __ipow__(self, other, modulo=None):  # **= operator
        return self.numeric_value ** other

    def __rpow__(self, other, modulo=None):  # ** operator
        return other ** self.numeric_value

    def __lt__(self, other):  # < (less than) operator
        return self.numeric_value < other

    def __gt__(self, other):  # > (greater than) operator
        return self.numeric_value > other

    def __le__(self, other):  # <= (less than or equal to) operator
        return self.numeric_value <= other

    def __ge__(self, other):  # >= (greater than or equal to) operator
        return self.numeric_value >= other

    def __eq__(self, other):  # == (equal to) operator
        return self.numeric_value == other

    def __and__(self, other):  # and (equal to) operator
        return self.numeric_value and other

    def __iand__(self, other):  # and (equal to) operator
        return self.numeric_value and other

    def __rand__(self, other):  # and (equal to) operator
        return other and self.numeric_value

    def __or__(self, other):  # or (equal to) operator
        return self.numeric_value or other

    def __ior__(self, other):  # or (equal to) operator
        return self.numeric_value or other

    def __ror__(self, other):  # or (equal to) operator
        return other or self.numeric_value

    # endregion

    # region conversion function
    def __abs__(self):
        return self.numeric_value.__abs__()

    def __bool__(self):
        return self.numeric_value.__bool__()

    def __str__(self):
        return self.value.__str__()

    def __int__(self):
        return self.numeric_value.__int__()

    def __ceil__(self):
        return self.numeric_value.__ceil__()

    def __round__(self, n=None):
        return self.numeric_value.__round__(n)
    # endregion
