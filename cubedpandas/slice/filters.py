# CubedPandas - Copyright (c)2024, Thomas Zeutschler, see LICENSE file

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

    @property
    def row_mask(self) -> np.ndarray | None:
        """
        Returns the row mask of all combined filters.
        """
        if len(self) == 0:
            return None
        return self[-1].context.row_mask  # the last filter is the most recent/filtered one

    def append(self, __object):
        super().append(__object)
        # todo: new filters need to be intersected with the last available filter
        return self