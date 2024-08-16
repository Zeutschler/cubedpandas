
from __future__ import annotations
import numpy as np
import pandas as pd


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
