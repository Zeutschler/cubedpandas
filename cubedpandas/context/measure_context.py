# CubedPandas - Copyright (c)2024, Thomas Zeutschler, see LICENSE file

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from cubedpandas.context.context import Context

if TYPE_CHECKING:
    from cubedpandas.cube import Cube
    from cubedpandas.schema.measure import Measure
    from cubedpandas.schema.dimension import Dimension


class MeasureContext(Context):
    """
    A context representing a measure of the cube.
    """

    def __init__(self, cube: Cube, parent: Context | None = None, address: Any = None, row_mask: np.ndarray | None = None,
                 measure: Measure | None = None, dimension: Dimension | None = None, resolve: bool = True,
                 filtered: bool = False):
        self._filtered: bool = filtered
        super().__init__(cube=cube, address=address, parent=parent, row_mask=row_mask,
                         measure=measure, dimension=dimension, resolve=resolve, filtered=filtered)
