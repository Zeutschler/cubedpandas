# CubedPandas - Copyright (c)2024, Thomas Zeutschler, see LICENSE file

from __future__ import annotations
from collections.abc import Iterable

from cubedpandas.slice.block_item import BlockItem

class Block:
    """
    Defines a block within an axis of a slice. Blocks contain 1 to M BlockSets, which are
    sets of dimension members.

    A slice consists of 2 axes, rows and columns. Each axis is divided into 0 to N blocks,
    which by themselves are defined by 1 to M sets of dimension members and/or measures.
    Block are independent of each other and can contain and reference different members
    from different dimensions or measures.
    """
    def __init__(self, name: str, data):
        self._name = name
        self._data = data
        self._block_items = BlockItems()
        if isinstance(data, (list, tuple)):
            for item in data:
                block_item = BlockItem(item)
                self._block_items.append(block_item)
        else:
            block_item = BlockItem(data)
            self._block_items.append(block_item)

    @property
    def block_items(self) -> BlockItems:
        return self._block_items

    def contains_any(self, data_type) -> bool:
        return any([block_set.contains_any(data_type) for block_set in self._block_items])


class BlockItems(Iterable[BlockItem]):
    """
    Defines an axis in a slice.

    A slice consists of 2 axes, rows and columns. Each axis is divided into 0 to N blocks,
    which by themselves are defined by 1 to M sets of dimension members and/or measures.
    Block are independent of each other and can contain and reference different members
    from different dimensions or measures.
    """
    def __init__(self):
        self._items: list[BlockItem] = []
        self._iterator: int = 0

    # Iterable and slice method
    def __iter__(self):
        self._iterator = 0
        return self

    def __next__(self):
        if self._iterator < len(self._items):
            block = self._items[self._iterator]
            self._iterator += 1
            return block
        else:
            raise StopIteration

    def __len__(self):
        return len(self._items)

    def __getitem__(self, key: int) -> BlockItem:
        return self._items[key]

    def append(self, item: BlockItem):
        self._items.append(item)
        return self

    def to_list(self) -> list:
        return self._items