import datetime
from abc import ABC
from typing import Iterable, Self
import numpy as np
from hybrid_dict import HybridDict
import pandas as pd

class Measure:
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