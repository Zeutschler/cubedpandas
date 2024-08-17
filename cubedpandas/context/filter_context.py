from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from cubedpandas.context.context import Context

if TYPE_CHECKING:
    from cubedpandas.measure import Measure
    from cubedpandas.dimension import Dimension

    from cubedpandas.context.context import MeasureContext


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

    def _compare(self, operator: str, other) -> 'MeasureContext':
        from cubedpandas.context.measure_context import MeasureContext
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