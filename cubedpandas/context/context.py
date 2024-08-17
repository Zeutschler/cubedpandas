# CubedPandas - Copyright (c)2024 by Thomas Zeutschler, BSD 3-clause license, see file LICENSE included in this package.

from __future__ import annotations
from typing import SupportsFloat, TYPE_CHECKING, Any

import numpy as np
import pandas as pd


# ___noinspection PyProtectedMember
if TYPE_CHECKING:
    from cubedpandas.cube import Cube
    from cubedpandas.slice import Slice
    from cubedpandas.measure import Measure
    from cubedpandas.dimension import Dimension

    # all subclasses of Context listed here:
    from cubedpandas.context.compound_context import CompoundContext
    from cubedpandas.context.boolean_operation_context import BooleanOperationContext, BooleanOperationContextEnum
    from cubedpandas.context.filter_context import FilterContext
    from cubedpandas.context.measure_context import MeasureContext
    from cubedpandas.context.context_resolver import ContextResolver

from cubedpandas.cube_aggregation import (CubeAggregationFunctionType,
                                          CubeAllocationFunctionType)
from cubedpandas.measure import Measure
from context.expression import Expression


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
    def __init__(self, cube: 'Cube', address: Any, parent: 'Context' | None = None,
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
            from cubedpandas.context.context_resolver import ContextResolver
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

    def by(self, rows: Any, columns: Any | None = None) -> 'CompoundContext':
        """Returns """
        from cubedpandas.context.compound_context import CompoundContext
        return CompoundContext(self, self[rows, columns])

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
        from cubedpandas.context.filter_context import FilterContext

        if self._semaphore:
            return super().__getattr__(name)
            # raise AttributeError(f"Unexpected fatal error while trying to resolve the context for '{name}'."
            #                     f"Likely due to multithreading issues. Please report this issue to the developer.")
        from cubedpandas.context.context_resolver import ContextResolver
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
        from cubedpandas.context.context_resolver import ContextResolver
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
            from cubedpandas.context.filter_context import FilterContext
            context = FilterContext(self)
            return context < other
        return self.numeric_value < other

    def __gt__(self, other):  # > (greater than) operator
        if isinstance(self, MeasureContext) and self.filtered:
            from cubedpandas.context.filter_context import FilterContext
            context = FilterContext(self)
            return context > other
        return self.numeric_value > other

    def __le__(self, other):  # <= (less than or equal to) operator
        from cubedpandas.context.measure_context import MeasureContext
        if isinstance(self, MeasureContext) and self.filtered:
            from cubedpandas.context.filter_context import FilterContext
            context = FilterContext(self)
            return context <= other
        return self.numeric_value <= other

    def __ge__(self, other):  # >= (greater than or equal to) operator
        from cubedpandas.context.measure_context import MeasureContext
        if isinstance(self, MeasureContext) and self.filtered:
            from cubedpandas.context.filter_context import FilterContext
            context = FilterContext(self)
            return context >= other
        return self.numeric_value >= other

    def __eq__(self, other):  # == (equal to) operator
        from cubedpandas.context.measure_context import MeasureContext
        if isinstance(self, MeasureContext) and self.filtered:
            from cubedpandas.context.filter_context import FilterContext
            context = FilterContext(self)
            return context == other
        return self.numeric_value == other

    def __ne__(self, other):  # != (not equal to) operator
        from cubedpandas.context.measure_context import MeasureContext
        if isinstance(self, MeasureContext) and self.filtered:
            from cubedpandas.context.filter_context import FilterContext
            context = FilterContext(self)
            return context != other
        return self.numeric_value != other

    def __and__(self, other):  # AND operator (A & B)
        if isinstance(other, Context):
            from cubedpandas.context.boolean_operation_context import BooleanOperationContext, BooleanOperationContextEnum
            return BooleanOperationContext(self, other, BooleanOperationContextEnum.AND)
        return self.numeric_value and other

    def __iand__(self, other):  # inplace AND operator (a &= b)
        if isinstance(other, Context):
            from cubedpandas.context.boolean_operation_context import BooleanOperationContext, BooleanOperationContextEnum
            return BooleanOperationContext(self, other, BooleanOperationContextEnum.AND)
        return self.numeric_value and other

    def __rand__(self, other):  # and operator
        if isinstance(other, Context):
            from cubedpandas.context.boolean_operation_context import BooleanOperationContext, BooleanOperationContextEnum
            return BooleanOperationContext(self, other, BooleanOperationContextEnum.AND)
        return self.numeric_value and other

    def __or__(self, other):  # OR operator (A | B)
        if isinstance(other, Context):
            from cubedpandas.context.boolean_operation_context import BooleanOperationContext, BooleanOperationContextEnum
            return BooleanOperationContext(self, other, BooleanOperationContextEnum.OR)
        return self.numeric_value or other

    def __ior__(self, other):  # inplace OR operator (A |= B)
        if isinstance(other, Context):
            from cubedpandas.context.boolean_operation_context import BooleanOperationContext, BooleanOperationContextEnum
            return BooleanOperationContext(self, other, BooleanOperationContextEnum.OR)
        return self.numeric_value or other

    def __ror__(self, other):  # or operator
        if isinstance(other, Context):
            from cubedpandas.context.boolean_operation_context import BooleanOperationContext, BooleanOperationContextEnum
            return BooleanOperationContext(self, other, BooleanOperationContextEnum.OR)
        return other or self.numeric_value

    def __xor__(self, other):  # xor operator
        if isinstance(other, Context):
            from cubedpandas.context.boolean_operation_context import BooleanOperationContext, BooleanOperationContextEnum
            return BooleanOperationContext(self, other, BooleanOperationContextEnum.XOR)
        return self._value ^ other

    def __invert__(self):  # ~ operator
        # Special case: NOT operation > inverts the row mask
        from cubedpandas.context.boolean_operation_context import BooleanOperationContext, BooleanOperationContextEnum
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
