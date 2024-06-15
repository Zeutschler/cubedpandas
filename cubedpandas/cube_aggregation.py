# slice.py
# CubedPandas - Multi-dimensional data analysis for Pandas dataframes.
# ©2024 by Thomas Zeutschler. All rights reserved.
# MIT License - please see the LICENSE file that should have been included in this package.

from enum import IntEnum
from typing import SupportsFloat, TYPE_CHECKING
import numpy as np


class CubeAllocationFunctionType(IntEnum):
    """
    Allocation functions supported for value write back in a cube.
    """
    DISTRIBUTE = 1  # distribute the value to all affected records based on the current distribution
    SET = 2         # set the value to all affected records
    DELTA = 3       # add the value to all affected records
    MULTIPLY = 4    # multiply the value with all affected records
    ZERO = 5        # set the value to zero to all affected records
    NAN = 6         # set the value to NaN to all affected records
    DEL = 7         # delete all affected records / rows


class CubeAggregationFunctionType(IntEnum):
    """
    Aggregation functions supported for the value in a cube.
    """
    SUM = 1
    AVG = 2
    MEDIAN = 3
    MIN = 4
    MAX = 5
    COUNT = 6
    STD = 7
    VAR = 8
    POF = 9
    NAN = 10
    AN = 11
    ZERO = 12
    NZERO = 13


class CubeAggregationFunction(SupportsFloat):
    """
    Represents aggregation functions, like SUM, MIN, MAX, VAG etc.,
    which are provided through the 'Cube' and 'Cell' object, e.g. by cube.avg["Apple", "Online"].
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
        if self._row_mask is None:
            return self._cube[None]
        return self._cube._evaluate(self._row_mask, self._measure,  self._op)

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

    def __truediv__(self, other):  # / operator (returns an float)
        return self.numeric_value / other

    def __idiv__(self, other):  # /= operator (returns an float)
        return self.numeric_value / other

    def __rtruediv__(self, other):  # / operator (returns an float)
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
    # endregion