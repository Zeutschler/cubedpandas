# todo: DEPRECATED CODE - TO BE REMOVED ON CLEANUP
# CubedPandas - Copyright (c)2024 by Thomas Zeutschler, BSD 3-clause license, see file LICENSE included in this package.

from __future__ import annotations
from typing import SupportsFloat, TYPE_CHECKING, Any
import numpy as np
import pandas as pd

# ___noinspection PyProtectedMember
if TYPE_CHECKING:
    from cubedpandas.cube import Cube, CubeAggregationFunction
    from cubedpandas.slice import Slice
    from cubedpandas.measure import Measure
    from cubedpandas.dimension import Dimension
    from cubedpandas.filter import Filter, DimensionFilter, MeasureFilter, CompoundFilter, CellFilter,  FilterOperation

from cubedpandas.cube_aggregation import CubeAggregationFunctionType, CubeAggregationFunction, \
    CubeAllocationFunctionType
from cubedpandas.measure import Measure


class Cell(SupportsFloat):
    """
    A cell represents a multi-dimensional data cell or area from within a cube. Cell objects can
    be used to navigate and access the data of a cube and thereby the underlying dataframe.

    Cells behave like Python floats and return a numeric aggregation of the
    underlying data. They are intended to be used in mathematical operations.

    Samples:
        >>> cdf = cubed(df)
        >>> value = cdf.A + cdf.B / 2
        200
        >>> cdf.A *= 2
    """

    # region Initialization
    def __init__(self, cube: Cube, address: Any, parent: Cell | None = None, row_mask: np.ndarray | None = None,
                 measure: str | None = None,
                 dynamic_access: bool = False):
        """
        Initializes a new Cell object. Not indented for direct use, but for internal use only.
        Args:
            cube:
                The cube object the cell is referring to.
            address:
                The address the cell is referring to.
            parent:
                (optional) A parent Cell for chaining
            row_mask:
                (optional) A row mask to filter the data for the cell.
            measure:
                (optional) A measure to calculate the value of the cell.
            dynamic_access:
                Identifies if the cell is accessed dynamically. e.g.: cube.Online.Apple.cost

        Returns:
            A new Cell object.

        Raises:
            ValueError:
                If the address is invalid and does not refer to a
                dimension, member or measure of the cube.
        """
        self._dynamic_call: bool = dynamic_access
        self._cube: Cube = cube
        self._parent: Cell = parent
        self._address = address
        if row_mask is None and measure is None:
            row_mask, measure = cube._resolve_address(address)
        else:
            row_mask, measure = self._cube._resolve_address_modifier(address, row_mask, measure, dynamic_access)
        self._row_mask: np.ndarray | None = row_mask
        self._measure: Measure = measure

    def __new__(cls, *args, **kwargs):
        return SupportsFloat.__new__(cls)

    # endregion

    # region Public Properties
    @property
    def value(self):
        """
        Returns:
             The sum value of the current cell from the underlying cube.
        """
        agg_function = CubeAggregationFunctionType.SUM
        if self._row_mask is None:
            if self._dynamic_call:
                return self._cube.df[self._measure.column].sum()
            else:
                return self._cube[self._address]
        else:
            return self._cube._evaluate(self._row_mask, self._measure, agg_function)

    @value.setter
    def value(self, value):
        """
        Writes a value of the current cell to the underlying cube.
        """
        allocation_function = CubeAllocationFunctionType.DISTRIBUTE
        if self._row_mask is None:
            self._cube[self._address] = value
        else:
            self._cube._allocate(self._row_mask, self._measure, value, allocation_function)

    @property
    def numeric_value(self) -> float:
        """
        Returns:
             The numerical value of the current cell from the underlying cube.
        """
        if self._row_mask is None:
            if self._measure is None:
                value = self._cube[self._address]
            else:
                value = self._cube._evaluate(self._row_mask, self._measure)
        else:
            value = self._cube._evaluate(self._row_mask, self._measure)
        if isinstance(value, (int, float, np.integer, np.floating, bool)):
            return float(value)
        else:
            return 0.0

    @property
    def cube(self):
        """
        Returns:
             The Cube object the Cell belongs to.
        """
        return self._cube

    @property
    def df(self) -> pd.DataFrame:
        """Returns:
        A new Pandas dataframe with all column, as the underlying dataframe
        of the Cube, but only with the rows that are represented by the cell.

        The returned dataframe is always a copy of the original dataframe, even if
        the cell is not filtering any rows from the underlying dataframe. The returned
        dataframe can be used for further processing outside the cube.

        """
        if self._row_mask is None:
            return self._cube.df.copy()
        return self._cube.df.iloc[self._row_mask]

    @property
    def address(self) -> any:
        """
        Returns:
            The partial address of the cell, as defined by the user
            This does not include the addresses defined by predecessor
            cells down to the cube.
        """
        return self._address

    def cube_address(self) -> any:
        """
        Returns:
            The full address of the cell, including all predecessor
            cells down to the cube.
        """
        if self._parent is not None:
            return f"{self._parent.cube_address}:{self._address}"
        return self._address

    @property
    def measure(self) -> Measure:
        """
        Returns:
            The Measure object the Cell is currently referring to.
            The measure refers to a column in the underlying dataframe
            that is used to calculate the value of the cell.
        """
        return self._measure


    @property
    def as_filter(self) -> Filter:
        """
        Returns:
            Converts the cell object into a filter object.
            The filter can be used of subsequently slicing the cube.
        """
        from cubedpandas.filter import CellFilter
        return CellFilter(parent=self)

    @property
    def _(self):
        """
        Returns:
            Converts the cell object into a filter object.
            The filter can be used of subsequently slicing the cube.
        """
        from cubedpandas.filter import CellFilter
        return CellFilter(parent=self)

    @property
    def mask(self) -> np.ndarray:
        """
        Returns:
            The row mask of the cell. The row mask is a list (Numpy ndarray)
            of the indexes of the rows represented by the cell. The row mask can be used
            for subsequent processing of the underlying dataframe outside the cube.
        """
        return self._row_mask

    @property
    def mask_inverse(self) -> np.ndarray:
        """
        Returns:
            The inverted row mask of the cell. The inverted row mask is a list (Numpy ndarray)
            of the indexes of the rows NOT represented by the cell. The inverted row mask
            can be used for subsequent processing of the underlying dataframe outside the cube.
        """
        return np.setdiff1d(self._cube._df.index.to_numpy(), self._row_mask)

    # endregion

    # region - Dynamic attribute resolving
    def __getattr__(self, name) -> Cell:
        """
        Dynamically resolves member from the cube and predesessor cells.
        This enables a more natural access to the cube data using the
        Python dot notation.
        Args:
            name: Name of a member or measure in the cube.

        Returns:
            A Cell object that represents the cube data related to the address.

        Samples:
            >>> cdf = cubed(df)
            >>> cdf.Online.Apple.cost
            50
        """
        return Cell(self._cube, address=name, parent=self, row_mask=self._row_mask, measure=self._measure,
                    dynamic_access=True)

    # endregion

    # region Cell manipulation via indexing/slicing
    def __getitem__(self, address):
        """
        Returns a nested cell of the cube and for a given address.
        Subsequent nested cells can bee seen as subsequent filters upon the underlying dataframe.

        Args:
            address:
                A valid cube address.
                Please refer the documentation for further details.

        Returns:
            A Cell object that represents the cube data related to the address
            and all predecessor cells down to the cube.

        Raises:
            ValueError:
                If the address is not valid or can not be resolved.
        """

        row_mask, measure = self._cube._resolve_address(address, self._row_mask, self._measure)
        return self._cube._evaluate(row_mask, measure=measure)

    def __setitem__(self, address, value):
        """
        Sets a value for a given address in the cube.
        Args:
            address:
                A valid cube address.
                Please refer the documentation for further details.
            value:
                The value to be set for the data represented by the address.
        Raises:
            PermissionError:
                If write back is attempted on a read-only Cube.
        """
        row_mask, measure = self._cube._resolve_address(address, self._row_mask, self._measure)
        self._cube._write_back(row_mask, measure, value)

    def __delitem__(self, address):
        """
        Deletes the records represented by the given address from the underlying
        dataframe of the cube.
        Args:
            address:
                A valid cube address.
                Please refer the documentation for further details.
        Raises:
            PermissionError:
                If write back is attempted on a read-only Cube.
        """
        row_mask, measure = self._cube._resolve_address(address, self._row_mask, self._measure)
        self._cube._delete(row_mask, measure)

    def cell(self, address):
        """
        Returns a cell of the cube for a given address.
        Tip: Use indexed access `cell[ ... ]` for better readability.
        Args:
            address:
                A valid cube address.
                Please refer the documentation for further details.

        Returns:
            A Cell object that represents the cube data related to the address.

        Raises:
            ValueError:
                If the address is not valid or can not be resolved.
        """
        return Cell(self._cube, address=address, parent=None, row_mask=self._row_mask, measure=self._measure)

    def slice(self, rows=None, columns=None, filters=None, config=None) -> Slice:
        """
        Returns a new slice for the cell. A slice represents a table-alike view to data in the cube.
        Typically, a slice has rows, columns and filters, comparable to an Excel PivotTable.
        Useful for printing in Jupyter, visual data analysis and reporting purposes.
        Slices can be easily 'navigated' by setting and changing rows, columns and filters.

        Please refer to the documentation of the Slice class for further details.

        Args:
            rows:
                The rows of the slice. Can be one or more dimensions with or without a member definition,
                or no dimension.

            columns:
                The columns of the slice. Can be one or more dimensions with or without a member definition,
                or no dimension.

            filters:
                The filters of the slice. Can be one or more dimensions with or without a member definition,
                or no dimension.

            config:
                (optional) A slice configuration as a dictionary, a json string or a path to an existing
                file containing the configuration. Slice configurations can be used to define a more
                complex layout. Please refer to the documentation of the Slice class for further details.

        Samples:
            >>> cdf = cubed(df)
            >>> cdf.slice(rows="product", columns="region", filters={"year": 2020})
            ------------------------------------
            year: 2000
            ------------------------------------
            |         | (all) | North | South |
            ------------------------------------
            | (all)   |   550 |   300 |   250 |
            | Apple   |   200 |   100 |   100 |
            | Banana  |   350 |   200 |   150 |
        """
        return Slice(self, rows=rows, columns=columns, filters=filters, config=config)
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

    def __and__(self, other):  # AND operator (A & B)
        return self._boolean_op(other, "AND")

    def __iand__(self, other):  # inplace AND operator (a &= b)
        new_cell = self._boolean_op(other, "AND")
        if isinstance(new_cell, Cell):
            self._row_mask = new_cell._row_mask
        self._measure = new_cell._measure

    def __rand__(self, other):  # and operator
        return other and self.numeric_value

    def __or__(self, other):  # OR operator (A | B)
        return self.numeric_value or other

    def __ior__(self, other):  # inplace OR operator (A |= B)
        return self.numeric_value or other

    def __ror__(self, other):  # or operator
        return other or self.numeric_value

    def __xor__(self, other):  # xor operator
        return self._value ^ other

    def __ne__(self, other):  # != (not equal to) operator
        return self.numeric_value != other

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

    # region Aggregation functions
    @property
    def sum(self):
        """
        Returns:
            The sum of the values for a given address.
        """
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.SUM, self._row_mask, self._measure)

    @property
    def avg(self):
        """
        Returns:
            The average of the values for a given address.
        """
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.AVG, self._row_mask, self._measure)

    @property
    def median(self):
        """
        Returns:
             The median of the values for a given address.
        """
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.MEDIAN, self._row_mask, self._measure)

    @property
    def min(self):
        """
        Returns:
            The minimum value for a given address.
        """
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.MIN, self._row_mask, self._measure)

    @property
    def max(self):
        """
        Returns:
             The maximum value for a given address.
        """
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.MAX, self._row_mask, self._measure)

    @property
    def count(self):
        """
        Returns:
             The number of the records matching a given address.
        """
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.COUNT, self._row_mask, self._measure)

    @property
    def std(self):
        """
        Returns:
            The standard deviation of the values for a given address.
        """
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.STD, self._row_mask, self._measure)

    @property
    def var(self):
        """
        Returns:
            The variance of the values for a given address.
        """
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.VAR, self._row_mask, self._measure)

    @property
    def pof(self):
        """
        Returns:
            The percentage of the sum of values for a given address related to all values in the data frame.
        """
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.POF, self._row_mask, self._measure)

    @property
    def nan(self):
        """
        Returns:
            The number of non-numeric values for a given address. 'nan' stands for 'not a number'.
        """
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.NAN, self._row_mask, self._measure)

    @property
    def an(self):
        """
        Returns:
            The number of numeric values for a given address. 'an' stands for 'a number'.
        """
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.AN, self._row_mask, self._measure)

    @property
    def zero(self):
        """
        Returns:
            The number of zero values for a given address. 'nan' stands for 'not a number'.
        """
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.ZERO, self._row_mask, self._measure)

    @property
    def nzero(self):
        """
        Returns:
            The number of non-zero values for a given address. 'an' stands for 'a number'.
        """
        return CubeAggregationFunction(self._cube, CubeAggregationFunctionType.NZERO, self._row_mask, self._measure)
    # endregion
