# CubedPandas - Copyright (c)2024 by Thomas Zeutschler, BSD 3-clause license, see LICENSE file.

from __future__ import annotations
from cubedpandas.slice.filter import Filter
import numpy as np

class Filters(list[Filter]):
    """
    Defines the filters of a slice.

    A slice consists of 2 axes, rows and columns. Each axis is divided into 0 to N blocks,
    which by themselves are defined by 1 to M sets of dimension members and/or measures.
    Block are independent of each other and can contain and reference different members
    from different dimensions or measures.
    """
    def __init__(self):
        super().__init__()

    def row_mask(self) -> np.ndarray | None:
        """
        Returns the row mask of all combined filters.
        """
        return self[-1].context.row_mask

    def append(self, __object):
        super().append(__object)
        # todo: new filters need to be intersected with the last available filter
        return self