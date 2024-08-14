
from __future__ import annotations
import numpy as np
import pandas as pd
from cubedpandas.filter import Filter, FilterOperation, DimensionFilter, MeasureFilter


class Measure:
    """
    Represents a measure within a Cube. Each measure is mapped to a column in the underlying Pandas dataframe.
    """
    # todo: add support for aliases
    def __init__(self, df: pd.DataFrame, column):
        self._df: pd.DataFrame = df
        self._column = column
        self._column_ordinal = df.columns.get_loc(column)
        self._dtype = df[column].dtype
        self._values: np.ndarray | None = None
        self._aliases: list[str] = []

    @property
    def column(self):
        """
        Returns the column name in underlying Pandas dataframe the measure refers to.
        """
        return self._column

    @property
    def df(self) -> pd.DataFrame:
        """
        Returns the underlying Pandas dataframe of the cube.
        """
        return self._df

    def __len__(self):
        return len(self._df)

    def __str__(self):
        return self._column

    def __repr__(self):
        return self._column

    def __eq__(self, other):
        if isinstance(other, str):
            return self._column == other
        return self._column == other._column and self._df.equals(other._df)

    def __gt__(self, other):
        filter = MeasureFilter(parent=self, expression=other, operation=FilterOperation.GT)
        return filter

    def __ge__(self, other):
        filter = MeasureFilter(parent=self, expression=other, operation=FilterOperation.GE)
        return filter

    def __lt__(self, other):
        filter = MeasureFilter(parent=self, expression=other, operation=FilterOperation.LT)
        return filter

    def __le__(self, other):
        filter = MeasureFilter(parent=self, expression=other, operation=FilterOperation.LE)
        return filter

    def __ne__(self, other):
        filter = MeasureFilter(parent=self, expression=other, operation=FilterOperation.NE)
        return filter
