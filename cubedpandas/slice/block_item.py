# CubedPandas - Copyright (c)2024, Thomas Zeutschler, see LICENSE file
from typing import Any


class BlockItem:
    """
    A BlockItem defines either a set of dimension members from one dimension or a set of measures.
    Think of BlockItems are nested member lists like in a pivot table.

    A slice consists of 2 axes, rows and columns. Each axis is divided into 0 to N blocks,
    which by themselves are defined by 1 to M sets of dimension members and/or measures.
    Block are independent of each other and can contain and reference different members
    from different dimensions or measures.
    """
    def __init__(self, item):
        self._item: Any = item
        self._iterator: int = 0

    def contains_any(self, data_type) -> bool:
        if isinstance(data_type, (list, tuple)):
            return any([isinstance(self._item, dt) for dt in data_type])
        return isinstance(self._item, data_type)

    @property
    def item(self) -> Any:
        return self._item

    @item.setter
    def item(self, item: Any):
        self._item = item
