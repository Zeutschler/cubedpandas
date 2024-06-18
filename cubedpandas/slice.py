# CubedPandas - Copyright (c)2024 by Thomas Zeutschler, BSD 3-clause license, see file LICENSE included in this package.

from __future__ import annotations
from typing import SupportsFloat, TYPE_CHECKING, Any
import numpy as np
from cubedpandas.cell import Cell

# ___noinspection PyProtectedMember
if TYPE_CHECKING:
    from cubedpandas.cube import Cube, CubeAggregationFunction

from cubedpandas.cube_aggregation import CubeAggregationFunctionType, CubeAggregationFunction, CubeAllocationFunctionType


class Slice:
    """A slice represents a view on a cube, and allows for easy access to the underlying Pandas dataframe.
    Typically, a slice has rows, columns and filter, just like in an Excel PivotTable. Slices
    are easy to define and use for convenient data analysis."""
    def __init__(self, cell:Cell, rows: Any = None, columns: Any = None,
                 filters: Any = None, config: dict | str | None = None):
        self.cell = cell
        self.rows = rows
        self.columns = columns
        self.filters = filters
        self.config = config