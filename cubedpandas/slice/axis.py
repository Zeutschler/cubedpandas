# CubedPandas - Copyright (c)2024, Thomas Zeutschler, see LICENSE file

from __future__ import annotations
from collections.abc import Iterable

from cubedpandas.slice.block import Block

class Axis:
    def __init__(self, name: str, data):
        self._name = name
        self._data = data
        self._axis_blocks = AxisBlocks()
        self._axis_blocks.append(Block(name, data))

    @property
    def blocks(self) -> AxisBlocks:
        return self._axis_blocks

    def contains_any(self, data_type) -> bool:
        return any([block.contains_any(data_type) for block in self._axis_blocks])


class AxisBlocks(Iterable[Block]):
    """
    Defines an axis in a slice.

    A slice consists of 2 axes, rows and columns. Each axis is divided into 0 to N blocks,
    which by themselves are defined by 1 to M sets of dimension members and/or measures.
    Block are independent of each other and can contain and reference different members
    from different dimensions or measures.
    """
    def __init__(self):
        self._blocks: list[Block] = []
        self._iterator: int = 0

    # Iterable and slice method
    def __iter__(self):
        self._iterator = 0
        return self

    def __next__(self):
        if self._iterator < len(self._blocks):
            block = self._blocks[self._iterator]
            self._iterator += 1
            return block
        else:
            raise StopIteration

    def __len__(self):
        return len(self._blocks)

    def __getitem__(self, key: int) -> Block:
        return self._blocks[key]

    def append(self, block: Block):
        self._blocks.append(block)
        return self