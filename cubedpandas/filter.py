# todo: DEPRECATED CODE - TO BE REMOVED ON CLEANUP
from __future__ import annotations

from enum import Enum, IntEnum
from typing import SupportsFloat, TYPE_CHECKING, Any
import numpy as np
import pandas as pd
import sortednp as snp   # https://sortednp.dev/guide/

# ___noinspection PyProtectedMember
if TYPE_CHECKING:
    from cubedpandas.cube import Cube, CubeAggregationFunction
    from cubedpandas.measure import Measure
    from cubedpandas.dimension import Dimension
    from cubedpandas.cell import Cell

class FilterOperation(IntEnum):
    AND = 0
    OR = 1
    XOR = 2
    NOT = 3
    SUB = 4
    GT = 5
    GE = 6
    LT = 7
    LE = 8
    NE = 9
    EQ = 10
    NONE = 99

class Filter:
    """
    A Filter for a CubedPandas dimension or measure, representing a column in the underlying Pandas dataframe.
    Filters can be combined using boolean operators to create more complex filters. Filters are evaluated lazily.
    """
    def __init__(self, parent, expression: Any, operation: FilterOperation = FilterOperation.AND):

        self._parent = parent
        self._other:Filter | None = None
        self._mask: np.ndarray | None = None
        self._operation: FilterOperation = operation
        self._expression = expression

    @property
    def df(self) -> pd.DataFrame:
        """
        Returns the underlying dataframe.
        """
        return self._parent.df

    @property
    def column(self):
        """
        Returns the column of the underlying dataframe related to the filter.
        """
        return self._parent.column

    @property
    def expression(self):
        return self._expression

    @property
    def mask(self) -> np.ndarray:  #, other: Filter | np.ndarray | None = None, op: FilterOperation = FilterOperation.AND) -> np.ndarray:
        """
        Evaluates the filter and returns a boolean mask for the underlying dataframe.

        Parameters:
            other: Another filter to be applied before combining the filters.

        Returns:
            A ndarray containing the index of those records that match the filter and all previous filters.
        """

        # Mask already available?
        if self._mask is not None:
            return self._mask

        # Evaluate the mask
        df = self.df
        if df is None:
            raise ValueError(f"No data to filter. Parent object of type '{type(self._parent)}' does not contain a dataframe.")

        # check arguments
        if isinstance(self._parent, CellFilter):
            column: str = self._parent.column
            parent_mask: np.ndarray = self._parent._parent.mask
            if self._other is not None:
                self._expression = self._other
        else:
            if hasattr(self._parent, 'property'):
                column: str = self._parent.column
            else:
                column: str = self.column
            if self._other is not None and not isinstance(self._other, Filter):
                raise ValueError(f"Unsupported filter argument '{self._other}'. You may have tried "
                                 f"to combine a filter with a non-filter object, e.g. a cell value instead of a filter.")

            # column: str = self._parent.column
            parent_mask: np.ndarray | None = self._parent.mask if isinstance(self._parent, Filter) else None

        if parent_mask is not None and self._operation >= FilterOperation.GT:
            df = df.loc[parent_mask, column]


        match self._operation:
            # boolean operations between 2 filters
            case FilterOperation.AND:
                mask_new = snp.intersect(parent_mask , self._other.mask, duplicates=snp.IntersectDuplicates.DROP)
                self._mask = np.intersect1d(parent_mask , self._other.mask)
                if not np.array_equal(mask_new, self._mask):
                    raise ValueError(f"Error in mask calculation for {self._operation}.")
            case FilterOperation.OR:
                mask_new = snp.merge(parent_mask , self._other.mask, duplicates=snp.MergeDuplicates.DROP)
                self._mask = np.union1d(parent_mask, self._other.mask)
                if not np.array_equal(mask_new, self._mask):
                    raise ValueError(f"Error in mask calculation for {self._operation}.")
            case FilterOperation.XOR:
                self._mask = np.setxor1d(parent_mask, self._other.mask)
            case FilterOperation.NOT:
                self._mask = np.setdiff1d(self._parent.df.index.to_numpy(), parent_mask)
            case FilterOperation.SUB:
                self._mask = np.setdiff1d(parent_mask, self._other.mask)

            # comparison operations between a filter and a value
            case FilterOperation.GT:
                self._mask = df[df[column] > self._expression].index.to_numpy()
            case FilterOperation.GE:
                self._mask = df[df[column] >= self._expression].index.to_numpy()
            case FilterOperation.LT:
                self._mask = df[df[column] < self._expression].index.to_numpy()
            case FilterOperation.LE:
                self._mask = df[df[column] <= self._expression].index.to_numpy()
            case FilterOperation.NE:
                self._mask = df[df[column] != self._expression].index.to_numpy()
            case FilterOperation.EQ:
                self._mask = df[df[column] == self._expression].index.to_numpy()

            # no operation, likely called by a CellFilter
            case FilterOperation.NONE:
                self._mask = df.index.to_numpy()

            case _:
                raise ValueError(f"Unsupported filter operation '{self._operation}'.")

        return self._mask

    @property
    def dimensions(self) -> list[Dimension]:
        """
        Returns the dimensions represented by the filter.
        """
        from cubedpandas.dimension import Dimension
        from cubedpandas.measure import Measure
        dims = []
        if isinstance(self._parent, Dimension):
            dims.append(self._parent)
        elif not isinstance(self._parent, Measure):
            dims.append(self._parent.dimensions)
        return dims


    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return f"Filter({self._parent} >>> {self._expression}) := {self.mask}"

    def __eq__(self, other):
        if isinstance(other, Filter):
            if len(self.mask) != len(other.mask):
                return False
            return set(self.mask) == set(other.mask)
        if isinstance(other, str):
            return self._expression == other

    def __gt__(self, other):
        return CompoundFilter(self, other, FilterOperation.GT)
    def __ge__(self, other):
        return CompoundFilter(self, other, FilterOperation.GE)
    def __lt__(self, other):
        return CompoundFilter(self, other, FilterOperation.LT)
    def __le__(self, other):
        return CompoundFilter(self, other, FilterOperation.LE)
    def __ne__(self, other):
        return CompoundFilter(self, other, FilterOperation.NE)

    def __and__(self, other) -> Filter:
        return CompoundFilter(self, other, FilterOperation.AND)
    def __iand__(self, other):
        return CompoundFilter(self, other, FilterOperation.AND)
    def __rand__(self, other):
        return CompoundFilter(self, other, FilterOperation.AND)

    def __or__(self, other):
        return CompoundFilter(self, other, FilterOperation.OR)
    def __ior__(self, other):
        return CompoundFilter(self, other, FilterOperation.OR)
    def __ror__(self, other):
        return CompoundFilter(self, other, FilterOperation.OR)

    def __xor__(self, other):
        return CompoundFilter(self, other, FilterOperation.XOR)
    def __ixor__(self, other):
        return CompoundFilter(self, other, FilterOperation.XOR)
    def __rxor__(self, other):
        return CompoundFilter(self, other, FilterOperation.XOR)

    def __invert__(self):
        return CompoundFilter(self, None, FilterOperation.NOT)

    def __neg__(self):
        """Inversion of the filter. Same as NOT operation."""
        return CompoundFilter(self, None, FilterOperation.NOT)

    def __add__(self, other):
        return CompoundFilter(self, other, FilterOperation.OR)
    def __iadd__(self, other):
        return CompoundFilter(self, other, FilterOperation.OR)
    def __radd__(self, other):
        return CompoundFilter(self, other, FilterOperation.OR)
    
    def __sub__(self, other):
        return CompoundFilter(self, other, FilterOperation.SUB)
    def __isub__(self, other):
        return CompoundFilter(self, other, FilterOperation.SUB)
    def __rsub__(self, other):
        return CompoundFilter(self, other, FilterOperation.SUB)
        

    def __nonzero__(self):
        return False

class DimensionFilter(Filter):

    def __init__(self, parent: Dimension, expression, operation: FilterOperation = FilterOperation.EQ):
        super().__init__(parent=parent, expression=expression, operation=operation)
        self._dimension: Dimension = parent

    @property
    def df(self) -> pd.DataFrame:
        """
        Returns the underlying dataframe.
        """
        return self._dimension._df

    @property
    def column(self):
        """
        Returns the column of the underlying dataframe related to the filter.
        """
        return self._dimension._column

    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return f"DimensionFilter({self._dimension}) := {self._expression})) >>> {self.mask}"


class MeasureFilter(Filter):
    def __init__(self, parent: Measure, expression, operation: FilterOperation = FilterOperation.EQ):
        super().__init__(parent=parent, expression=expression, operation=operation)
        self._measure: Measure = parent

    @property
    def df(self) -> pd.DataFrame:
        """
        Returns:
            Returns the underlying dataframe.
        """
        return self._measure._df

    @property
    def column(self):
        """
        Returns the column of the underlying dataframe related to the filter.
        """
        return self._measure._column

    def __repr__(self):
        return f"DimensionFilter({self._dimension}) := {self._expression})) >>> {self.mask}"

class CellFilter(Filter):
    def __init__(self, parent: Cell):
        super().__init__(parent=parent, expression=None, operation=FilterOperation.NONE)
        self._mask = parent.mask

    @property
    def df(self) -> pd.DataFrame:
        """
        Returns:
            Returns the underlying dataframe.
        """
        return self._parent.cube.df

    @property
    def column(self):
        """
        Returns the column of the underlying dataframe related to the filter.
        """
        return self._parent.measure.column

    def __repr__(self):
        return f"CellFilter({self._parent.address}) >>> {self.mask}"

class CompoundFilter(Filter):

    def __init__(self, one: Filter, other: Filter | None, operation: FilterOperation = FilterOperation.AND):
        super().__init__(parent=one, expression=None, operation=operation)
        self._parent = one
        self._other = other
        self._operation = operation
        self._mask: np.ndarray | None = None

    @property
    def df(self) -> pd.DataFrame:
        """
        Returns the underlying dataframe.
        """
        return self._parent._parent.df

    @property
    def column(self):
        """
        Returns the column of the underlying dataframe related to the filter.
        """
        return self._parent.column

    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        op = f"{self._operation}".split(".")[1].upper() if self._operation is not None else "AND"
        return f"CompoundFilter({self._one} {op} {self._other}) >>> {self.mask}"
