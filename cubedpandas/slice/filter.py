
from __future__ import annotations

class Filter:
    """
    Defines a filter of a slice. Either a single measure or a set of dimension members from one dimension.

    A slice consists of 2 axes, rows and columns. Each axis is divided into 0 to N blocks,
    which by themselves are defined by 1 to M sets of dimension members and/or measures.
    Block are independent of each other and can contain and reference different members
    from different dimensions or measures.
    """
    pass
