
from __future__ import annotations
from cubedpandas.slice.block_set import BlockSet

class Block(list[BlockSet]):
    """
    Defines a block within an axis of a slice. Blocks contain 1 to M BlockSets, which are
    sets of dimension members.

    A slice consists of 2 axes, rows and columns. Each axis is divided into 0 to N blocks,
    which by themselves are defined by 1 to M sets of dimension members and/or measures.
    Block are independent of each other and can contain and reference different members
    from different dimensions or measures.
    """
    pass