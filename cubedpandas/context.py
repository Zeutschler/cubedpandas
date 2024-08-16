# CubedPandas - Copyright (c)2024 by Thomas Zeutschler, BSD 3-clause license, see file LICENSE included in this package.

from __future__ import annotations

import datetime
from collections.abc import Iterable
from enum import IntEnum
from typing import SupportsFloat, TYPE_CHECKING, Any
import numpy as np
import pandas as pd


# ___noinspection PyProtectedMember
if TYPE_CHECKING:
    from cubedpandas.cube import Cube, CubeAggregationFunction
    from cubedpandas.slice import Slice
    from cubedpandas.measure import Measure
    from cubedpandas.dimension import Dimension
    from cubedpandas.member import Member, MemberSet
    # from cubedpandas.context_resolver import ContextResolver, ExpressionContextResolver

from cubedpandas.cube_aggregation import (CubeAggregationFunctionType,
                                          CubeAggregationFunction,
                                          CubeAllocationFunctionType)
from cubedpandas.member import Member, MemberSet
from cubedpandas.measure import Measure
from cubedpandas.expression import Expression
from cubedpandas.date_parser import parse_date


class Context(SupportsFloat):
    """
    A context represents a multi-dimensional data context or area from within a cube. Context objects can
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
    def __init__(self, cube: Cube, address: Any, parent: Context | None = None,
                 row_mask: np.ndarray | None = None, member_mask: np.ndarray | None = None,
                 measure: str | None | Measure = None, dimension: str | None | Dimension = None,
                 resolve: bool = True, filtered: bool = False):
        """
        Initializes a new Context object. For internal use only.
        Raises:
            ValueError:
                If the address is invalid and does not refer to a
                dimension, member or measure of the cube.
        """
        self._use_new_approach: bool = True  # for DEV purposes only...

        self._semaphore: bool = False
        self._cube: Cube = cube
        self._address = address
        self._parent: Context = parent
        self._df = cube.df
        self._row_mask: np.ndarray | None = row_mask
        self._member_mask: np.ndarray | None = member_mask
        self._measure: Measure | None = measure
        self._dimension: Dimension | None = dimension
        self._convert_values_to_python_data_types: bool = True
        self._filtered: bool = filtered

        if resolve and cube.eager_evaluation:
            resolved = ContextResolver.resolve(parent=self, address=address, dynamic_attribute=False)
            self._row_mask = resolved.row_mask
            self._measure = resolved.measure
            self._dimension = resolved.dimension

    def __new__(cls, *args, **kwargs):
        return SupportsFloat.__new__(cls)

    # endregion

    # region Public properties and methods
    @property
    def value(self):
        """
        Returns:
             The sum value of the current context from the underlying cube.
        """
        return self._evaluate(self._row_mask, self._measure, CubeAggregationFunctionType.SUM)

    @value.setter
    def value(self, value):
        """
        Writes a value of the current context to the underlying cube.
        """
        allocation_function = CubeAllocationFunctionType.DISTRIBUTE
        if self._row_mask is None:
            self._cube[self._address] = value
        else:
            self._cube._allocate(self.mask, self.measure, value, allocation_function)

    @property
    def numeric_value(self) -> float:
        """
        Returns:
             The numerical value of the current context from the underlying cube.
        """
        value = self._evaluate(self._row_mask, self._measure, CubeAggregationFunctionType.SUM)
        if isinstance(value, (float, np.floating)):
            return float(value)
        if isinstance(value, (int, np.integer, bool)):
            return int(value)
        else:
            return 0.0

    @property
    def cube(self) -> Cube:
        """
        Returns:
             The Cube object the Context belongs to.
        """
        return self._cube

    @property
    def dimension(self) -> Dimension:
        """
        Returns:
             The Cube object the Context belongs to.
        """
        return self._dimension

    @property
    def parent(self) -> Context:
        """
        Returns:
             The parent Context of the current Context. If the current Context is the root Context of the cube,
             then the parent Context will be `None`.
        """
        return self._parent

    @property
    def df(self) -> pd.DataFrame:
        """Returns:
        Returns a new Pandas dataframe with all column of the underlying dataframe
        of the Cube, but only with the rows that are represented by the current context.

        The returned dataframe is always a copy of the original dataframe, even if
        the context is not filtering any rows from the underlying dataframe. The returned
        dataframe can be used for further processing outside the cube.

        """
        if self._row_mask is None:
            return self._cube.df  #
        return self._cube.df.iloc[self._row_mask]

    @property
    def address(self) -> any:
        """
        Returns:
            The partial address of the context, as defined by the user
            This does not include the addresses defined by predecessor
            cells down to the cube.
        """
        return self._address

    def cube_address(self) -> any:
        """
        Returns:
            The full address of the context, including all predecessor
            cells down to the cube.
        """
        if self._parent is not None:
            return f"{self._parent.cube_address}:{self._address}"
        return self._address

    @property
    def measure(self) -> Measure:
        """
        Returns:
            The Measure object the Context is currently referring to.
            The measure refers to a column in the underlying dataframe
            that is used to calculate the value of the context.
        """
        return self._measure

    @measure.setter
    def measure(self, value: Measure):
        self._measure = value

    @property
    def filtered(self) -> bool:
        return self._filtered

    @property
    def mask(self) -> np.ndarray | None:
        """
        Returns:
            The row mask of the context. The row mask is represented by a Numpy ndarray
            of the indexes of the rows represented by the current context. The row mask can be used
            for subsequent processing of the underlying dataframe outside the cube.
        """
        return self._row_mask

    @property
    def row_mask(self) -> np.ndarray | None:
        """
        Returns:
            The row mask of the context. The row mask is represented by a Numpy ndarray
            of the indexes of the rows represented by the current context. The row mask can be used
            for subsequent processing of the underlying dataframe outside the cube.
        """
        return self._row_mask

    @property
    def member_mask(self) -> np.ndarray | None:
        """
        Returns:
            The member mask of the context. If the context refers to a member or a set of members from a dimension.
            then a Numpy ndarray containing the indexes of the rows representing the members is returned.
            `None` is returned otherwise.
            The row mask can be used for subsequent processing of the underlying dataframe outside the cube.
        """
        return self._member_mask

    def get_row_mask(self, before_dimension: Dimension | None) -> np.ndarray | None:
        if self._dimension != before_dimension:
            return self._row_mask
        if self._parent is not None:
            return self._parent.get_row_mask(before_dimension)
        else:
            return None

    @property
    def mask_inverse(self) -> np.ndarray:
        """
        Returns:
            The inverted row mask of the context. The inverted row mask is represented by a Numpy ndarray
            of the indexes of the rows NOT represented by the current context. The inverted row mask
            can be used for subsequent processing of the underlying dataframe outside the cube.
        """
        return np.setdiff1d(self._cube._df.index.to_numpy(), self._row_mask)

    # endregion

    # region - Dynamic attribute resolving
    def __getattr__(self, name) -> Context:
        """Dynamically resolves member from the cube and predecessor cells."""
        # remark: This pseudo-semaphore is not threadsafe but needed to prevent infinite __getattr__ loops.
        if self._semaphore:
            return super().__getattr__(name)
            # raise AttributeError(f"Unexpected fatal error while trying to resolve the context for '{name}'."
            #                     f"Likely due to multithreading issues. Please report this issue to the developer.")
        self._semaphore = True
        if str(name).endswith("_"):
            name = str(name)[:-1]
            if name != "":
                context = ContextResolver.resolve(parent=self, address=name, dynamic_attribute=True)
                resolved = FilterContext(context)
            else:
                resolved = FilterContext(self)
        else:
            resolved = ContextResolver.resolve(parent=self, address=name, dynamic_attribute=True)
        self._semaphore = False
        return resolved

    # endregion

    # region Context manipulation via indexing/slicing
    def __getitem__(self, address):
        """
        Returns a nested context of the cube and for a given address.
        Subsequent nested cells can bee seen as subsequent filters upon the underlying dataframe.

        Args:
            address:
                A valid cube address.
                Please refer the documentation for further details.

        Returns:
            A Context object that represents the cube data related to the address
            and all predecessor cells down to the cube.

        Raises:
            ValueError:
                If the address is not valid or can not be resolved.
        """
        return ContextResolver.resolve(parent=self, address=address)

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
        raise NotImplementedError("Write back is not yet implemented.")
        # row_mask, measure = self._cube._resolve_address(address, self.mask, self.measure)
        # self._cube._write_back(row_mask, measure, value)

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
        row_mask, measure = self._cube._resolve_address(address, self.mask, self.measure)
        self._cube._delete(row_mask, measure)

    def slice(self, rows=None, columns=None, filters=None, config=None) -> Slice:
        """
        Returns a new slice for the context. A slice represents a table-alike view to data in the cube.
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

    def filter(self, expression: Any) -> Context:
        """
        Filters the current context by a given expression.
        Args:
            expression:
                The expression to be used for filtering the context.
        Returns:
            A new context with the filtered data.
        """
        raise NotImplementedError("Filtering is not yet implemented.")
        if isinstance(expression, str):
            expression = Expression(expression)
        row_mask = expression.evaluate(self._df)
        return Context(self._cube, self._address, self, row_mask=row_mask)

    # endregion

    # region Evaluation functions
    def _resolve_measure(self) -> Measure:
        """
        Resolves the measure for the current context.
        Returns:
            The resolved Measure object.
        """
        if self._measure is None:
            if self._parent is None:
                self._measure = self._cube.measures.default
            else:
                self._measure = self._parent._resolve_measure()
        return self._measure

    def _evaluate(self, row_mask, measure, operation: CubeAggregationFunctionType = CubeAggregationFunctionType.SUM):
        # Evaluates the value of the current context.
        # Note: This method uses and operates directly on internal Numpy ndarray used by the
        # underlying Pandas dataframe. Therefore, no expensive data copying is required.

        # Get a reference to the underlying Numpy ndarray for the current measure column.
        if measure is None:
            # Resolve the measure if not provided.
            measure = self._resolve_measure()
            if measure is None:
                # The cube has no measures defined
                # So we simply count the number of records.
                if row_mask is None:
                    return len(self._df.index)
                return len(row_mask)

        if row_mask is not None and row_mask.size == 0:  # no records found
            if ((operation >= CubeAggregationFunctionType.COUNT) or
                    pd.api.types.is_integer_dtype(self._df[measure.column])):
                return 0  # return default value
            else:
                return 0.0  # return default value

        # Get and filter the values array by the row mask.
        values = self._df[measure.column].to_numpy()
        if row_mask is not None:
            values: np.ndarray = values[row_mask]

        # Evaluate the final value based on the aggregation operation.
        match operation:
            case CubeAggregationFunctionType.SUM:
                value = np.nansum(values)
            case CubeAggregationFunctionType.AVG:
                value = np.nanmean(values)
            case CubeAggregationFunctionType.MEDIAN:
                value = np.nanmedian(values)
            case CubeAggregationFunctionType.MIN:
                value = np.nanmin(values)
            case CubeAggregationFunctionType.MAX:
                value = np.nanmax(values)
            case CubeAggregationFunctionType.COUNT:
                value = len(values)
            case CubeAggregationFunctionType.STD:
                value = np.nanstd(values)
            case CubeAggregationFunctionType.VAR:
                value = np.nanvar(values)
            case CubeAggregationFunctionType.POF:
                value = float(np.nansum(values)) / float(self.cube.df[str(measure)].sum())
            case CubeAggregationFunctionType.NAN:
                value = np.count_nonzero(np.isnan(values))
            case CubeAggregationFunctionType.AN:
                value = np.count_nonzero(~np.isnan(values))
            case CubeAggregationFunctionType.ZERO:
                value = np.count_nonzero(values == 0)
            case CubeAggregationFunctionType.NZERO:
                value = np.count_nonzero(values)
            case _:
                value = np.nansum(values)  # default operation is SUM

        # Convert the value from Numpy to Python data type if required.
        if self._convert_values_to_python_data_types:
            value = self._convert_to_python_type(value)
        return value

    @staticmethod
    def _convert_to_python_type(value):
        if isinstance(value, (np.integer, int)):
            return int(value)
        elif isinstance(value, (np.floating, float)):
            return float(value)
        elif isinstance(value, (np.datetime64, pd.Timestamp)):
            return pd.Timestamp(value).to_pydatetime()
        elif isinstance(value, (np.bool_, bool)):
            return bool(value)
        elif isinstance(value, (np.ndarray, pd.Series, list, tuple)):
            if isinstance(value, np.ndarray):
                value = value.tolist()
            return [Context._convert_to_python_type(v) for v in value]
        else:
            return value

    # endregion

    # region Operator overloading and float behaviour
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
        if isinstance(self, MeasureContext) and self.filtered:
            context = FilterContext(self)
            return context < other
        return self.numeric_value < other

    def __gt__(self, other):  # > (greater than) operator
        if isinstance(self, MeasureContext) and self.filtered:
            context = FilterContext(self)
            return context > other
        return self.numeric_value > other

    def __le__(self, other):  # <= (less than or equal to) operator
        if isinstance(self, MeasureContext) and self.filtered:
            context = FilterContext(self)
            return context <= other
        return self.numeric_value <= other

    def __ge__(self, other):  # >= (greater than or equal to) operator
        if isinstance(self, MeasureContext) and self.filtered:
            context = FilterContext(self)
            return context >= other
        return self.numeric_value >= other

    def __eq__(self, other):  # == (equal to) operator
        if isinstance(self, MeasureContext) and self.filtered:
            # curframe = inspect.currentframe()
            # calframe = inspect.getouterframes(curframe, 2)
            # print(f">>> called by '{calframe[1][3]}')'")
            context = FilterContext(self)
            return context == other
        return self.numeric_value == other

    def __ne__(self, other):  # != (not equal to) operator
        if isinstance(self, MeasureContext) and self.filtered:
            context = FilterContext(self)
            return context != other
        return self.numeric_value != other

    def __and__(self, other):  # AND operator (A & B)
        if isinstance(other, Context):
            return BooleanOperationContext(self, other, BooleanOperationContextEnum.AND)
        return self.numeric_value and other

    def __iand__(self, other):  # inplace AND operator (a &= b)
        if isinstance(other, Context):
            return BooleanOperationContext(self, other, BooleanOperationContextEnum.AND)
        return self.numeric_value and other

    def __rand__(self, other):  # and operator
        if isinstance(other, Context):
            return BooleanOperationContext(self, other, BooleanOperationContextEnum.AND)
        return self.numeric_value and other

    def __or__(self, other):  # OR operator (A | B)
        if isinstance(other, Context):
            return BooleanOperationContext(self, other, BooleanOperationContextEnum.OR)
        return self.numeric_value or other

    def __ior__(self, other):  # inplace OR operator (A |= B)
        if isinstance(other, Context):
            return BooleanOperationContext(self, other, BooleanOperationContextEnum.OR)
        return self.numeric_value or other

    def __ror__(self, other):  # or operator
        if isinstance(other, Context):
            return BooleanOperationContext(self, other, BooleanOperationContextEnum.OR)
        return other or self.numeric_value

    def __xor__(self, other):  # xor operator
        if isinstance(other, Context):
            return BooleanOperationContext(self, other, BooleanOperationContextEnum.XOR)
        return self._value ^ other

    def __invert__(self):  # ~ operator
        # Special case: NOT operation > inverts the row mask
        return BooleanOperationContext(self, operation=BooleanOperationContextEnum.NOT)

    # endregion

    # region conversion function
    def __abs__(self):
        return self.numeric_value.__abs__()

    def __bool__(self):
        return self.numeric_value.__bool__()

    def __str__(self):
        return self.value.__str__()

    def __repr__(self):
        return self.value.__str__()

        t = ""
        if self._dimension is not None:
            t += f"{self.dimension}:{self.address}"
        elif self._address is not None:
            t += f"{self._address}"
        else:
            t += f"*"
        if not self.value is None:
            t += f" = {self.value.__str__()}"
        else:
            t += f" = None"

        if isinstance(self._parent, Context):
            t += f" <<< {self.parent.__repr__()}"
        return t

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
        return self.value.__format__(format_spec)

    # endregion

    # region Aggregation functions
    @property
    def sum(self):
        """
        Returns:
            The sum of the values for a given address.
        """
        return self._evaluate(self._row_mask, self._measure, CubeAggregationFunctionType.SUM)

    @property
    def avg(self):
        """
        Returns:
            The average of the values for a given address.
        """
        return self._evaluate(self._row_mask, self._measure, CubeAggregationFunctionType.AVG)

    @property
    def median(self):
        """
        Returns:
             The median of the values for a given address.
        """
        return self._evaluate(self._row_mask, self._measure, CubeAggregationFunctionType.MEDIAN)

    @property
    def min(self):
        """
        Returns:
            The minimum value for a given address.
        """
        return self._evaluate(self._row_mask, self._measure, CubeAggregationFunctionType.MIN)

    @property
    def max(self):
        """
        Returns:
             The maximum value for a given address.
        """
        return self._evaluate(self._row_mask, self._measure, CubeAggregationFunctionType.MAX)

    @property
    def count(self):
        """
        Returns:
             The number of the records matching a given address.
        """
        return self._evaluate(self._row_mask, self._measure, CubeAggregationFunctionType.COUNT)

    @property
    def std(self):
        """
        Returns:
            The standard deviation of the values for a given address.
        """
        return self._evaluate(self._row_mask, self._measure, CubeAggregationFunctionType.STD)

    @property
    def var(self):
        """
        Returns:
            The variance of the values for a given address.
        """
        return self._evaluate(self._row_mask, self._measure, CubeAggregationFunctionType.VAR)

    @property
    def pof(self):
        """
        Returns:
            The percentage of the sum of values for a given address related to all values in the data frame.
        """
        return self._evaluate(self._row_mask, self._measure, CubeAggregationFunctionType.POF)

    @property
    def nan(self):
        """
        Returns:
            The number of non-numeric values for a given address. 'nan' stands for 'not a number'.
        """
        return self._evaluate(self._row_mask, self._measure, CubeAggregationFunctionType.NAN)

    @property
    def an(self):
        """
        Returns:
            The number of numeric values for a given address. 'an' stands for 'a number'.
        """
        return self._evaluate(self._row_mask, self._measure, CubeAggregationFunctionType.AN)

    @property
    def zero(self):
        """
        Returns:
            The number of zero values for a given address. 'nan' stands for 'not a number'.
        """
        return self._evaluate(self._row_mask, self._measure, CubeAggregationFunctionType.ZERO)

    @property
    def nzero(self):
        """
        Returns:
            The number of non-zero values for a given address. 'an' stands for 'a number'.
        """
        return self._evaluate(self._row_mask, self._measure, CubeAggregationFunctionType.NZERO)
    # endregion

    # region Utility functions

    # endregion


class CubeContext(Context):
    """
    A context representing the cube itself.
    """

    def __init__(self, cube: Cube):
        super().__init__(cube=cube, address=None, parent=None, row_mask=None, measure=None)
        self._measure = cube.measures.default


class ContextContext(Context):
    """
    A context representing by an existing context
    """

    def __init__(self, parent: Context, nested: Context):
        # merge the row masks of the parent and the nested context, e.g. parent[nested]
        if parent.dimension == nested.dimension:
            parent_row_mask = parent.get_row_mask(before_dimension=parent.dimension)
            member_mask = np.union1d(parent.member_mask, nested.member_mask)
            if parent_row_mask is None:
                row_mask = member_mask
            else:
                row_mask = np.intersect1d(parent_row_mask, member_mask, assume_unique=True)
        elif isinstance(nested.parent, FilterContext):
            if parent.row_mask is None:
                row_mask = nested.row_mask
            elif nested.row_mask is None:
                row_mask = parent.row_mask
            else:
                row_mask = np.intersect1d(parent.row_mask, nested.row_mask, assume_unique=True)
        else:
            member_mask = nested.member_mask
            if parent.row_mask is None:
                row_mask = nested.row_mask
            else:
                row_mask = np.intersect1d(parent.row_mask, member_mask, assume_unique=True)

        super().__init__(cube=parent.cube, address=nested.address, parent=parent,
                         row_mask=row_mask, member_mask=nested.member_mask,
                         measure=nested.measure, dimension=nested.dimension,
                         resolve=False)
        self._referenced_context = nested

        @property
        def referenced_context(self):
            return self._referenced_context


class BooleanOperationContextEnum(IntEnum):
    AND = 1
    OR = 2
    XOR = 3
    NOT = 4


class BooleanOperationContext(Context):
    """ A context representing a boolean operation between two Context objects."""

    def __init__(self, left: Context, right: Context | None = None,
                 operation: BooleanOperationContextEnum = BooleanOperationContextEnum.AND):
        self._left: Context = left
        self._right: Context | None = right
        self._operation: BooleanOperationContextEnum = operation
        match self._operation:
            case BooleanOperationContextEnum.AND:
                row_mask = np.intersect1d(left.row_mask, right.row_mask, assume_unique=True)
            case BooleanOperationContextEnum.OR:
                row_mask = np.union1d(left.row_mask, right.row_mask)
            case BooleanOperationContextEnum.XOR:
                row_mask = np.setxor1d(left.row_mask, right.row_mask, assume_unique=True)
            case BooleanOperationContextEnum.NOT:
                row_mask = np.setdiff1d(left._df.index.to_numpy(), left.row_mask, assume_unique=True)
            case _:
                raise ValueError(f"Invalid boolean operation '{operation}'. Only 'AND', 'OR' and 'XOR' are supported.")

        if self._operation == BooleanOperationContextEnum.NOT:
            # unary operation
            super().__init__(cube=left.cube, address=None, parent=left.parent,
                             row_mask=row_mask, member_mask=None,
                             measure=left.measure, dimension=left.dimension, resolve=False)
        else:
            # binary operations
            super().__init__(cube=right.cube, address=None, parent=left.parent,
                             row_mask=row_mask, member_mask=None,
                             measure=right.measure, dimension=right.dimension, resolve=False)

        @property
        def left(self) -> Context:
            return self._left

        @property
        def right(self) -> Context | None:
            return self._right

        @property
        def operation(self) -> BooleanOperationContextEnum:
            return self._operation


class MeasureContext(Context):
    """
    A context representing a measure of the cube.
    """

    def __init__(self, cube: Cube, parent: Context | None, address: Any = None, row_mask: np.ndarray | None = None,
                 measure: Measure | None = None, dimension: Dimension | None = None, resolve: bool = True,
                 filtered: bool = False):
        self._filtered: bool = filtered
        super().__init__(cube=cube, address=address, parent=parent, row_mask=row_mask,
                         measure=measure, dimension=dimension, resolve=resolve, filtered=filtered)


class DimensionContext(Context):
    """
    A context representing a dimension of the cube.
    """

    def __init__(self, cube: Cube, parent: Context | None, address: Any = None, row_mask: np.ndarray | None = None,
                 measure: Measure | None = None, dimension: Dimension | None = None, resolve: bool = True):
        super().__init__(cube=cube, address=address, parent=parent, row_mask=row_mask,
                         measure=measure, dimension=dimension, resolve=resolve)


class MemberNotFoundContext(Context):
    """
    A context representing a member that was not found in the cube.
    """

    def __init__(self, cube: Cube, parent: Context | None, address: Any = None,
                 dimension: Dimension | None = None):
        empty_mask = pd.DataFrame(columns=["x"]).index.to_numpy()
        super().__init__(cube=cube, address=address, parent=parent, row_mask=empty_mask,
                         measure=parent.measure, dimension=dimension, resolve=False)


class MemberContext(Context):
    """
    A context representing a member or set of members of the cube.
    """

    # todo: implement something like: cdf.products[cdf.sales > 100]
    def __init__(self, cube: Cube, parent: Context | None, address: Any = None, row_mask: np.ndarray | None = None,
                 measure: Measure | None = None, dimension: Dimension | None = None,
                 members: MemberSet | None = None, member_mask: np.ndarray | None = None, resolve: bool = True):
        super().__init__(cube=cube, address=address, parent=parent, row_mask=row_mask,
                         measure=measure, dimension=dimension, resolve=resolve)
        self._members: MemberSet = members
        self._member_mask = member_mask

    @property
    def members(self) -> MemberSet:
        return self._members


class FilterContext(Context):
    """
    A context representing a filter on another context.
    """

    def __init__(self, parent: Context | None, filter_expression: Any = None, row_mask: np.ndarray | None = None,
                 measure: Measure | None = None, dimension: Dimension | None = None, resolve: bool = True):
        self._expression = filter_expression

        if row_mask is None:
            row_mask = parent.row_mask
        super().__init__(cube=parent.cube, address=filter_expression, parent=parent, row_mask=row_mask,
                         measure=parent.measure, dimension=parent.dimension, resolve=resolve)

    def _compare(self, operator: str, other) -> MeasureContext:
        try:
            match operator:
                case "<":
                    row_mask = self._df[self._df[self.measure.column] < other].index.to_numpy()
                    # print(f"{self.measure.column} < {other} := {row_mask}, {self._row_mask}")
                case "<=":
                    row_mask = self._df[self._df[self.measure.column] <= other].index.to_numpy()
                case ">":
                    row_mask = self._df[self._df[self.measure.column] > other].index.to_numpy()
                case ">=":
                    row_mask = self._df[self._df[self.measure.column] >= other].index.to_numpy()
                case "==":
                    row_mask = self._df[self._df[self.measure.column] == other].index.to_numpy()
                case "!=":
                    row_mask = self._df[self._df[self.measure.column] != other].index.to_numpy()
                case _:
                    raise ValueError(f"Unsupported comparison '{operator}'.")
        except TypeError as err:
            raise ValueError(f"Unsupported comparison '{operator}' of a Context with "
                             f"an object of type '{type(other)}' and value '{other}' .")

        if self._row_mask is not None:
            row_mask = np.intersect1d(self._row_mask, row_mask, assume_unique=True)
        self._expression = f"{self.measure} {operator} {other}"
        self._address = self._expression
        self._row_mask = row_mask
        return MeasureContext(cube=self.cube, address=self._expression, parent=self, row_mask=row_mask,
                              measure=self.measure, dimension=self.dimension, resolve=False, filtered=False)

    @property
    def expression(self) -> Any:
        return self._expression

    def __lt__(self, other) -> MeasureContext:  # < (less than) operator
        return self._compare("<", other)

    def __gt__(self, other) -> MeasureContext:  # > (greater than) operator
        return self._compare(">", other)

    def __le__(self, other) -> MeasureContext:  # <= (less than or equal to) operator
        return self._compare("<=", other)

    def __ge__(self, other) -> MeasureContext:  # >= (greater than or equal to) operator
        return self._compare(">=", other)

    def __eq__(self, other) -> MeasureContext:  # == (equal to) operator
        return self._compare("==", other)

    def __ne__(self, other) -> MeasureContext:  # != (not equal to) operator
        return self._compare("!=", other)


#
class ContextResolver:
    """A helper class to resolve the address of a context."""

    @staticmethod
    def resolve(parent: Context, address, dynamic_attribute: bool = False,
                target_dimension: Dimension | None = None) -> Context:

        # 1. If no address needs to be resolved, we can simply return the current/parent context.
        if address is None:
            return parent

        # unpack the parent context
        cube = parent.cube
        row_mask = parent.row_mask
        member_mask = parent.member_mask
        measure = parent.measure
        dimension = parent.dimension

        # 2. If the address is already a context, then we can simply wrap it into a ContextContext and return it.
        if isinstance(address, Context):
            if parent.cube == address.cube:
                return ContextContext(parent, address)
            raise ValueError(f"The context handed in as an address argument refers to a different cube/dataframe. "
                             f"Only contexts from the same cube can be used as address arguments.")

        # get the datatype of

        # 3. String addresses are resolved by checking for measures, dimensions and members.
        if isinstance(address, str):

            # 3.1. Check for names of measures
            if address in cube.measures:
                # set the measure for the context to the new resolved measure
                measure = cube.measures[address]
                resolved_context = MeasureContext(cube=cube, parent=parent, address=address, row_mask=row_mask,
                                                  measure=measure, dimension=dimension, resolve=False)
                return resolved_context
                # return ContextReference(context=resolved_context, address=address, row_mask=row_mask,
                #                        measure=measure, dimension=dimension)

            # 3.2. Check for names of dimensions
            if address in cube.dimensions:
                dimension = cube.dimensions[address]
                resolved_context = DimensionContext(cube=cube, parent=parent, address=address,
                                                    row_mask=row_mask,
                                                    measure=measure, dimension=dimension, resolve=False)
                return resolved_context
                # ref = ContextReference(context=resolved_context, address=address, row_mask=row_mask,
                #                       measure=measure, dimension=dimension)
                # return ref

            # 3.3. Check if the address contains a list of members, e.g. "A, B, C"
            address = ContextResolver.string_address_to_list(cube, address)

        # 4. Check for members of all data types over all dimensions in the cube
        #    Let's try start with a dimension that was handed in,
        #    if a dimension was handed in from the parent context.
        if not isinstance(address, list):

            skip_checks = False
            dimension_list = None
            dimension_switched = False

            # Check for dimension hints and leverage them, e.g. "products:apple", "children:1"
            if target_dimension is not None:
                dimension_list = [target_dimension]
            elif isinstance(address, str) and (":" in address):
                dim_name, member_name = address.split(":")
                if dim_name.strip() in cube.dimensions:
                    new_dimension = cube.dimensions[dim_name.strip()]
                    if dimension is not None:
                        dimension_switched = new_dimension != dimension
                    dimension = new_dimension

                    address = member_name.strip()  # todo: Datatype conversion required for int, bool, date?
                    dimension_list = [dimension]
                    skip_checks = True  # let's skip the checks as we have a dimension hint
            if dimension_list is None:
                dimension_list = cube.dimensions.starting_with_this_dimension(dimension)

            for dim in dimension_list:
                if dim == dimension and not dimension_switched:
                    # We are still at the dimension that was handed in, therefore we need to check for
                    # subsequent members from one dimension, e.g., if A, B, C are all members from the
                    # same dimension, then `cube.A.B.C` will require to join the member rows of A, B and C
                    # before we filter the rows from a previous context addressing another or no dimension.
                    if ContextResolver.matching_data_type(address, dim):
                        parent_row_mask = parent.get_row_mask(before_dimension=dimension)
                        exists, new_row_mask, member_mask = (
                            dimension._check_exists_and_resolve_member(address, parent_row_mask, member_mask,
                                                                       skip_checks=skip_checks))
                    else:
                        exists, new_row_mask, member_mask = False, None, None
                else:
                    # This indicates a dimension context switch,
                    # e.g. from `None` to dimension `A`, or from dimension `A` to dimension `B`.
                    exists, new_row_mask, member_mask = dim._check_exists_and_resolve_member(address, row_mask)

                if exists:
                    # We found the member...
                    member = Member(dim, address)
                    members = MemberSet(dimension=dim, address=address, row_mask=new_row_mask,
                                        members=[member])
                    resolved_context = MemberContext(cube=cube, parent=parent, address=address,
                                                     row_mask=new_row_mask, member_mask=member_mask,
                                                     measure=measure, dimension=dim,
                                                     members=members, resolve=False)
                    return resolved_context

        if not dynamic_attribute:
            # As we are NOT in a dynamic context like `cube.A.online.sales`, where only exact measure,
            # dimension and member names are supported, and have not yet found a suitable member, we need
            # to check for complex member set definitions like filter expressions, list, dictionaries etc.
            is_valid_context, new_context_ref = ContextResolver.resolve_complex(parent, address, dimension)
            if is_valid_context:
                return new_context_ref
            else:
                if parent.cube.ignore_member_key_errors and not dynamic_attribute:
                    if dimension is not None:
                        if cube.df[dimension.column].dtype == pd.DataFrame([address, ])[0].dtype:
                            return MemberNotFoundContext(cube=cube, parent=parent, address=address, dimension=dimension)

                raise ValueError(new_context_ref.message)

        # 4. If we've not yet resolved anything meaningful, then we need to raise an error...
        raise ValueError(f"Invalid member name or address '{address}'. "
                         f"Tip: check for typos and upper/lower case issues.")

    @staticmethod
    def resolve_complex(context: Context, address, dimension: Dimension | None = None) -> tuple[bool, Context]:
        """ Resolves complex member definitions like filter expressions, lists, dictionaries etc. """

        if dimension is None:
            dimension = context.dimension

        if isinstance(address, str):
            # 1. try wildcard expressions like "On*" > resolving e.g. to "Online"
            if "*" in address:
                if dimension is None:
                    if address == "*":
                        # This can only happen if we are still at the cube level, no dimension has been selected yet.
                        # In this case, we will return the cube context to return all records
                        return True, context
                    # We are at the cube level, so we need to consider all dimensions
                    dimensions = context.cube.dimensions
                else:
                    # We are at a dimension level, so we will only consider the current dimension
                    dimensions = [dimension]

                for dim in dimensions:
                    match_found, members = dim.wildcard_filter(address)

                    if match_found:
                        member_mask = None
                        parent_row_mask = context.get_row_mask(before_dimension=context.dimension)
                        exists, new_row_mask, member_mask = (
                            dim._check_exists_and_resolve_member(member=members, row_mask=parent_row_mask,
                                                                 parent_member_mask=member_mask,
                                                                 skip_checks=True))
                        if exists:
                            members = MemberSet(dimension=context.dimension, address=address, row_mask=new_row_mask,
                                                members=address)
                            resolved_context = MemberContext(cube=context.cube, parent=context, address=address,
                                                             row_mask=new_row_mask, member_mask=member_mask,
                                                             measure=context.measure, dimension=context.dimension,
                                                             members=members, resolve=False)
                            return True, resolved_context

            if dimension is not None and pd.api.types.is_datetime64_any_dtype(dimension.dtype):
                # 2. Date based filter expressions like "2021-01-01" or "2021-01-01 12:00:00"
                from_dt, to_dt = parse_date(address)
                if (from_dt, to_dt) != (None, None):

                    # We have a valid date or data range, let's resolve it
                    from_dt, to_dt = np.datetime64(from_dt), np.datetime64(to_dt)
                    parent_row_mask = context.get_row_mask(before_dimension=context.dimension)
                    exists, new_row_mask, member_mask = dimension._check_exists_and_resolve_member(
                        member=(from_dt, to_dt), row_mask=parent_row_mask, parent_member_mask=context.member_mask,
                        skip_checks=True, evaluate_as_range=True)
                    if exists:
                        members = MemberSet(dimension=context.dimension, address=address, row_mask=new_row_mask,
                                            members=address)
                        resolved_context = MemberContext(cube=context.cube, parent=context, address=address,
                                                         row_mask=new_row_mask, member_mask=member_mask,
                                                         measure=context.measure, dimension=context.dimension,
                                                         members=members, resolve=False)
                        return True, resolved_context

            # 3. String based filter expressions like "sales > 100" or "A, B, C"
            #    Let's try to parse the address as a Python-compliant expression from the given address
            exp: Expression = Expression(address)
            try:
                if exp.parse():
                    # We have a syntactically valid expression, so let's try to resolve/evaluate it
                    exp_resolver = ExpressionContextResolver(context, address)
                    new_context = exp.evaluate(exp_resolver)

                    if new_context is None:
                        # We have a valid expression, but it did not resolve to a context
                        context.message = (f"Failed to resolve address or expression '{address}'. "
                                           f"Maybe it tries to refer to a member name that does not exist "
                                           f"in any of the dimension of the cube.")
                        return False, context

                    if isinstance(new_context, Iterable):
                        new_context = list(new_context)[-1]
                    return True, new_context

                else:
                    # Expression parsing failed
                    context.message = f"Failed to resolve address or expression '{address}."
                    return False, context

            except ValueError as err:
                context.message = f"Failed to resolve address or expression '{address}. {err}"
                return False, context


        elif isinstance(address, dict):
            # 4. Dictionary based expressions like {"product": "A", "channel": "Online"}
            #    which are only supported for the CubeContext.
            if not isinstance(context, CubeContext):
                context.message = (f"Invalid address "
                                   f"'{address}'. Dictionary based addressing is not "
                                   f"supported for contexts representing a dimensions, members or measures.")
                return False, context

            # process all arguments of the dictionary
            for dim_name, member in address.items():
                if dim_name not in context.cube.dimensions:
                    context.message = (f"Invalid address '{address}'. Dictionary key '{dim_name}' does "
                                       f"not reference to a dimension (dataframe column name) defined "
                                       f"for the cube.")
                    return False, context
                dim = context.cube.dimensions[dim_name]
                # first add a dimension context...
                context = DimensionContext(cube=context.cube, parent=context, address=dim_name,
                                           row_mask=context.row_mask,
                                           measure=context.measure, dimension=dim, resolve=False)
                # ...then add the respective member context.
                # This approach is required 1) to be able to properly rebuild the address and 2) to
                # be able to apply the list-based member filters easily.
                context = ContextResolver.resolve(context, member, target_dimension=dim)
            return True, context


        elif isinstance(address, Iterable):
            # 5. List based expressions like ["A", "B", "C"] or (1, 2, 3)
            #    Conventions:
            #    - When applied to CubeContext: elements can be measures, dimensions or members
            #    - When applied to DimensionContext: elements can only be members of the current dimension
            #    - When applied to MemberContext: NOT SUPPORTED
            #    - When applied to MeasureContext: NOT SUPPORTED
            if isinstance(context, DimensionContext):
                # For increased performance, no individual upfront member checks will be made.
                # Instead, we the list as a whole will processed by numpy.
                member_mask = None
                parent_row_mask = context.get_row_mask(before_dimension=context.dimension)
                exists, new_row_mask, member_mask = (
                    context.dimension._check_exists_and_resolve_member(member=address, row_mask=parent_row_mask,
                                                                       parent_member_mask=member_mask,
                                                                       skip_checks=True))
                if not exists:
                    context.message = (f"Invalid member list '{address}'. "
                                       f"At least one member seems to be an unsupported unhashable object.")
                    return False, context

                members = MemberSet(dimension=context.dimension, address=address, row_mask=new_row_mask,
                                    members=address)
                resolved_context = MemberContext(cube=context.cube, parent=context, address=address,
                                                 row_mask=new_row_mask, member_mask=member_mask,
                                                 measure=context.measure, dimension=context.dimension,
                                                 members=members, resolve=False)
                return True, resolved_context

            elif isinstance(context, CubeContext):
                # ...for CubeContext we need to check for arbitrary measures, dimensions and members.
                for item in address:
                    context = ContextResolver.resolve(context, item)
                return True, context

            else:
                # ...for MemberContext and MeasureContext and ContextContext we need to raise an error.
                context.message = (f"Invalid address '{address}'. List or tuple based addressing is not "
                                   f"supported for contexts representing members, measures or referenced contexts.")
                return False, context

        context.message = (f"Invalid member name or address '{address}'. "
                           f"Tip: check for typos and upper/lower case issues.")
        return False, context

    @staticmethod
    def string_address_to_list(cube, address: str):
        delimiter = cube.settings.list_delimiter
        if not delimiter in address:
            return address
        address = address.split(delimiter)
        return [a.strip() for a in address]

    @staticmethod
    def merge_contexts(parent: Context, child: Context) -> Context:
        """Merges the rows of two contexts."""

        if parent.dimension == child.dimension:
            parent_row_mask = parent.get_row_mask(before_dimension=parent.dimension)
            child._member_mask = np.union1d(parent.member_mask, child.member_mask)
            child._row_mask = np.intersect1d(parent_row_mask, child._member_mask, assume_unique=True)

        else:
            child._row_mask = np.intersect1d(parent.row_mask, child._member_mask, assume_unique=True)

        return child

    @staticmethod
    def matching_data_type(address: any, dimension: Dimension) -> bool:
        """Checks if the address matches the data type of the dimension."""
        if isinstance(address, str):
            return pd.api.types.is_string_dtype(dimension.dtype) # pd.api.types.is_object_dtype((dimension.dtype)
        elif isinstance(address, int):
            return pd.api.types.is_integer_dtype(dimension.dtype)
        elif isinstance(address, (str, datetime.datetime, datetime.date)):
            return pd.api.types.is_datetime64_any_dtype(dimension.dtype)
        elif isinstance(address, float):
            return pd.api.types.is_float_dtype(dimension.dtype)
        elif isinstance(address, bool):
            return pd.api.types.is_bool_dtype(dimension.dtype)
        return False


class ExpressionContextResolver:
    """A helper class to provide the current context to Expressions."""

    def __init__(self, context: Context, address):
        self._context: Context | None = context
        self._address = address

    @property
    def context(self):
        return self._context

    def resolve(self, name: str) -> Context | None:
        if name == self._address:
            return None
        # Please note that the context is changing/extended every time a new context is resolved.
        self._context = self._context[name]
        return self._context
