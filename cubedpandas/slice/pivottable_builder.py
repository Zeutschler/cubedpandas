from enum import IntEnum

import pandas as pd
import numpy as np


class PivotTableStyle(IntEnum):
    PANDAS = 0
    """Pandas default style with no advanced formatting."""
    CUBEDPANDAS = 1
    """CubedPandas style with sub totals, number format guessing and advanced formatting."""


class PivotTableBuilder:
    """
    A helper class to build and manipulate Pandas pivot tables from dataframes.
    """

    def __init__(self, df: pd.DataFrame):
        self.df: pd.DataFrame = df
        self.pt: pd.DataFrame | None = None
        self._all_label: str = "(all)"

    def build(self, index, columns, values, aggfunc: str = "sum"):
        self.pt = self.df.pivot_table(index=index, columns=columns, values=values, aggfunc=aggfunc)
        return self

    @property
    def all_label(self):
        """
        Returns:
            The label for the 'all' value of totals and subtotals. Default value is '(all)'.
        """
        return self._all_label

    @all_label.setter
    def all_label(self, value):
        self._all_label = value
