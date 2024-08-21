# CubedPandas - Copyright (c)2024, Thomas Zeutschler, see LICENSE file

from __future__ import annotations
from typing import TYPE_CHECKING, Any
import numpy as np

from cubedpandas.context.enums import ContextFunction
from cubedpandas.context.context import Context

if TYPE_CHECKING:
    from cubedpandas.cube import Cube
    from cubedpandas.measure import Measure
    from cubedpandas.dimension import Dimension


class FunctionContext(Context):
    """
    A context representing a mathematical operation like SUM, MIN, MAX, AVG, etc.
    """
    KEYWORDS = {"SUM", "AVG", "MEDIAN", "MIN", "MAX", "STD", "VAR", "POF",
                "COUNT", "NAN", "AN", "ZERO", "NZERO", "CUSTOM"}


    def __init__(self, parent: Context | None = None, function: ContextFunction | str = ContextFunction.SUM):
        super().__init__(cube=parent.cube, address=parent.address, parent=parent, row_mask=parent.row_mask,
                         measure=parent.measure, dimension=parent.dimension, resolve=False, filtered=parent.is_filtered)

        if isinstance(function, str):
            try:
                function = ContextFunction[function.upper()]
            except KeyError:
                raise ValueError(f"Unknown function {function}. Supported functions are {FunctionContext.KEYWORDS}")

        self._function:ContextFunction = function

