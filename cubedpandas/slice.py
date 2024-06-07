from __future__ import annotations
from common import CubeAggregationFunctionType
from collections.abc import Iterable
from typing import SupportsFloat
import typing

import pandas as pd
import pyarrow as pa
import numpy as np

# noinspection PyProtectedMember

if typing.TYPE_CHECKING:
    from cube import Cube, CubeAggregationFunction


class Slice(SupportsFloat):
    """
    A slice represents a multi-dimensional data cell or range from within a cube. Slice objects can
    be used to navigate through and interact with the data space of a cube and the underlying dataframe.
    Slices behave like float values and can be directly used in mathematical calculations that read from
    or write to a cube.

    Sample usage:

    .. code:: python
        import cubedpandas as cpd

        df = get_your_dataframe()
        cube = cpd.Cube(df)

        # get a value from the cube and add 19% VAT
        net_value = cube.slice("2024", "Aug", "Germany", "NetSales")
        gross_sales_usa = net_value * 1.19

        # create new data or overwrite data for 2025 by copying all 2024 prices and adding 5% inflation
        cube.slice("2025", "Price") = cube.slice("2024", "Price") * 1.05
    """

    __slots__ = "_cube", "_address", "_row_mask", "_measure"

    #: Indicates that either subsequent rules should continue and do the calculation
    #: work or that the cell value, either from a base-level or an aggregated cell,
    #: form the underlying cube should be used.
    CONTINUE = object()
    #: Indicates that rules function was not able return a proper result (why ever).
    NONE = object()
    #: Indicates that the rules functions run into an error. Such errors will be
    #: pushed up to initially calling cell request.
    ERROR = object()

    # region Initialization
    @classmethod
    def create(cls, cube:Cube, address) -> Slice:
        slice = Slice()
        slice._cube  = cube
        slice._address = address
        slice._row_mask, slice._measure = cube._resolve_address(address)
        return slice

    def __init__(self):
        self._cube:Cube | None = None
        self._address = None
        self._row_mask: np.ndarray | None = None
        self._measure = None

    def __new__(cls):
        return SupportsFloat.__new__(cls)

    # endregion

    # region Properties
    @property
    def value(self):
        """Reads the value of the current cell idx_address from the underlying cube."""
        if self._row_mask is None:
            return self._cube[self._address]
        else:
            agg_function = CubeAggregationFunctionType.SUM
            return self._cube._evaluate(self._row_mask, self._measure, agg_function)

    @value.setter
    def value(self, value):
        """Writes a value of the current cell idx_address to the underlying cube."""
        self._cube[self._address] = value

    @property
    def numeric_value(self) -> float:
        """Reads the numeric value of the current cell idx_address from the underlying cube."""
        value = self._cube[self._address]
        if isinstance(value, (int, float, np.integer, np.floating, bool)):
            return float(value)
        else:
            return 0.0

    @property
    def cube(self):
        """Returns the cube the cell belongs to."""
        return self._cube

    # endregion


    # region Cell manipulation via indexing/slicing
    def __getitem__(self, address):
        row_mask, measure = self._cube._resolve_address_modifier(address, self._row_mask)
        return self._cube._evaluate(row_mask, measure=measure)

    def __setitem__(self, address, value):
        row_mask, measure = self._cube._resolve_address_modifier(address, self._row_mask)
        raise NotImplementedError("Slice.__setitem__ is not yet implemented.")

    def __delitem__(self, address):
        row_mask, measure = self._cube._resolve_address_modifier(address, self._row_mask)
        self._cube._delete(row_mask, measure)

    def slice(self, address):
        slice = Slice()
        slice._cube = self._cube
        slice._address = address
        slice._row_mask, slice._measure = self._cube._resolve_address_modifier(address, self._row_mask)
        return slice
    # endregion

    # region - Dynamic attribute resolving
    def __getattr__(self, name):
        name = str(name).replace("_", " ")
        return self.__getitem__(name)

    # def __getattribute__(*args):
    #     print("Class getattribute invoked")
    #     return object.__getattribute__(*args)
    # endregion

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

    #region Aggregation functions
    def sum(self):
        """Returns the sum of the values for a given address."""
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.SUM, self._row_mask)

    @property
    def avg(self):
        """Returns the average of the values for a given address."""
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.AVG, self._row_mask)

    @property
    def median(self):
        """Returns the median of the values for a given address."""
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.MEDIAN, self._row_mask)

    @property
    def min(self):
        """Returns the minimum value for a given address."""
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.MIN, self._row_mask)

    @property
    def max(self):
        """Returns the maximum value for a given address."""
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.MAX, self._row_mask)

    @property
    def count(self):
        """Returns the number of the records matching a given address."""
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.COUNT, self._row_mask)

    @property
    def stddev(self):
        """Returns the standard deviation of the values for a given address."""
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.STDDEV, self._row_mask)

    @property
    def var(self):
        """Returns the variance of the values for a given address."""
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.VAR, self._row_mask)

    @property
    def pof(self):
        """Returns the percentage of the sum of values for a given address related to all values in the data frame."""
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.POF, self._row_mask)

    @property
    def nan(self):
        """Returns the number of non-numeric values for a given address. 'nan' stands for 'not a number'"""
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.NAN, self._row_mask)

    @property
    def an(self):
        """Returns the number of numeric values for a given address. 'an' stands for 'a number'"""
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.AN, self._row_mask)
    # endregion
