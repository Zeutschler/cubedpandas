# measure.py
# CubedPandas - Multi-dimensional data analysis for Pandas dataframes.
# ©2024 by Thomas Zeutschler. All rights reserved.
# MIT License - please see the LICENSE file that should have been included in this package.

import numpy as np
import pandas as pd

class Measure:
    """
    Represents a measure within a Cube. Each measure is mapped to a column in the underlying Pandas dataframe.
    """

    def __init__(self, df: pd.DataFrame, column):
        self._df: pd.DataFrame = df
        self._column = column
        self._column_ordinal = df.columns.get_loc(column)
        self._dtype = df[column].dtype
        self._values: np.ndarray | None = None

    @property
    def column(self):
        return self._column

    def __len__(self):
        return len(self._df)

    def __str__(self):
        return self._column

    def __repr__(self):
        return self._column

    def __eq__(self, other):
        if isinstance(other, str):
            return self._column == other
        return  self._column == other._column and self._df.equals(other._df)
