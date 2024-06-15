# CubedPandas - Copyright (c)2024 by Thomas Zeutschler, BSD 3-clause license, see file LICENSE included in this package.

from __future__ import annotations
from typing import SupportsFloat, TYPE_CHECKING
import numpy as np

# ___noinspection PyProtectedMember
if TYPE_CHECKING:
    from cubedpandas.cube import Cube, CubeAggregationFunction

from cubedpandas.cube_aggregation import CubeAggregationFunctionType, CubeAggregationFunction, CubeAllocationFunctionType


class Slice:
    """A slice represents a view on a cube, and allows for easy access to the underlying Pandas dataframe.
    Typically, a slice has rows, columns and filter, just like in an Excel PivotTable. Slices
    are easy to define and use for convenient data analysis."""
    pass