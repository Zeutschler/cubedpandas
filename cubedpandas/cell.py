# cell.py
# CubedPandas - Multi-dimensional data analysis for Pandas dataframes.
# ©2024 by Thomas Zeutschler. All rights reserved.
# MIT License - please see the LICENSE file that should have been included in this package.

from __future__ import annotations
from typing import SupportsFloat, TYPE_CHECKING
import numpy as np

# ___noinspection PyProtectedMember
if TYPE_CHECKING:
    from cubedpandas.cube import Cube, CubeAggregationFunction

from cubedpandas.cube_aggregation import CubeAggregationFunctionType, CubeAggregationFunction, CubeAllocationFunctionType


class Cell(SupportsFloat):
    """
    A cell represents a multi-dimensional data cell or range from within a cube. Cell objects can
    be used to navigate through and interact with the data space of a cube and the underlying dataframe.
    Cells behave like float values and can be directly used in mathematical calculations that read from
    or write to a cube.

    Sample usage:

    .. code:: python
        import cubedpandas as cpd

        df = get_your_dataframe()
        cube = cpd.Cube(df)

        # get a value from the cube and add 19% VAT
        net_value = cube.cell("2024", "Aug", "Germany", "NetSales")
        gross_sales_usa = net_value * 1.19

        # create new data or overwrite data for 2025 by copying all 2024 prices and adding 5% inflation
        cube.cell("2025", "Price") = cube.cell("2024", "Price") * 1.05
    """

    __slots__ = "_cube", "_address", "_row_mask", "_measure", "_state", "_dynamic_call"

    # region Initialization
    def __init__(self, cube:Cube, address, row_mask:np.ndarray | None = None, measure:str | None = None,
                 dynamic_access:bool = False):
        self._dynamic_call:bool = dynamic_access
        self._cube:Cube = cube
        self._address = address
        if row_mask is None and measure is None:
            row_mask, measure = cube._resolve_address(address)
        else:
            row_mask, measure = self._cube._resolve_address_modifier(address, row_mask, measure, dynamic_access)
        self._row_mask: np.ndarray | None = row_mask
        self._measure = measure

    def __new__(cls, *args, **kwargs):
        return SupportsFloat.__new__(cls)
    # endregion

    # region Properties
    @property
    def value(self):
        """Returns the sum value of the current cell from the underlying cube."""
        agg_function = CubeAggregationFunctionType.SUM
        if self._row_mask is None:
            return self._cube[self._address]
        else:
            return self._cube._evaluate(self._row_mask, self._measure, agg_function)

    @value.setter
    def value(self, value):
        """Writes a value of the current cell to the underlying cube."""
        allocation_function = CubeAllocationFunctionType.DISTRIBUTE
        if self._row_mask is None:
            self._cube[self._address] = value
        else:
            self._cube._allocate(self._row_mask, self._measure, value, allocation_function)

    @property
    def numeric_value(self) -> float:
        """Returns the numeric value of the current cell from the underlying cube."""
        if self._row_mask is None:
            value = self._cube[self._address]
        else:
            value = self._cube._evaluate(self._row_mask, self._measure)
        if isinstance(value, (int, float, np.integer, np.floating, bool)):
            return float(value)
        else:
            return 0.0

    @property
    def cube(self):
        """Returns the cube the cell belongs to."""
        return self._cube

    @property
    def address(self):
        """Returns the address of the cell."""
        return self._address

    @property
    def measure(self):
        """Returns the measure of the cell."""
        return self._measure

    # region - Dynamic attribute resolving
    def __getattr__(self, name) -> Cell:
        # dynamic member / measure access e.g.: cube.Online.Apple.cost
        return Cell(self._cube, address=name, row_mask=self._row_mask, measure=self._measure, dynamic_access=True)
    # endregion

    # region Cell manipulation via indexing/slicing
    def __getitem__(self, address):
        row_mask, measure = self._cube._resolve_address(address, self._row_mask, self._measure)
        return self._cube._evaluate(row_mask, measure=measure)

    def __setitem__(self, address, value):
        row_mask, measure = self._cube._resolve_address(address, self._row_mask, self._measure)
        self._cube._write_back(row_mask, measure, value)

    def __delitem__(self, address):
        row_mask, measure = self._cube._resolve_address(address, self._row_mask, self._measure)
        self._cube._delete(row_mask, measure)


    def cell(self, address):
        return Cell(self._cube, address, self._row_mask, self._measure)
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

    def __repr__(self):
        return self.value.__repr__()

    def __round__(self, n=None):
        return self.numeric_value.__round__(n)

    def __trunc__(self):
        return self.numeric_value.__trunc__()

    def __floor__(self):
        return self.numeric_value.__floor__()

    def __int__(self):
        return self.numeric_value.__int__()

    def __ceil__(self):
        return self.numeric_value.__ceil__()

    def __format__(self, format_spec):
        # return self.numeric_value.__format__(format_spec)
        return self.value.__format__(format_spec)

    # endregion

    #region Aggregation functions
    @property
    def sum(self):
        """Returns the sum of the values for a given address."""
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.SUM, self._row_mask, self._measure)

    @property
    def avg(self):
        """Returns the average of the values for a given address."""
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.AVG, self._row_mask, self._measure)

    @property
    def median(self):
        """Returns the median of the values for a given address."""
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.MEDIAN, self._row_mask, self._measure)

    @property
    def min(self):
        """Returns the minimum value for a given address."""
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.MIN, self._row_mask, self._measure)

    @property
    def max(self):
        """Returns the maximum value for a given address."""
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.MAX, self._row_mask, self._measure)

    @property
    def count(self):
        """Returns the number of the records matching a given address."""
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.COUNT, self._row_mask, self._measure)

    @property
    def std(self):
        """Returns the standard deviation of the values for a given address."""
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.STD, self._row_mask, self._measure)

    @property
    def var(self):
        """Returns the variance of the values for a given address."""
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.VAR, self._row_mask, self._measure)

    @property
    def pof(self):
        """Returns the percentage of the sum of values for a given address related to all values in the data frame."""
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.POF, self._row_mask, self._measure)

    @property
    def nan(self):
        """Returns the number of non-numeric values for a given address. 'nan' stands for 'not a number'"""
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.NAN, self._row_mask, self._measure)

    @property
    def an(self):
        """Returns the number of numeric values for a given address. 'an' stands for 'a number'"""
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.AN, self._row_mask, self._measure)

    @property
    def zero(self):
        """Returns the number of zero values for a given address. 'nan' stands for 'not a number'"""
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.ZERO, self._row_mask, self._measure)

    @property
    def nzero(self):
        """Returns the number of non-zero values for a given address. 'an' stands for 'a number'"""
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.NZERO, self._row_mask, self._measure)
    # endregion
