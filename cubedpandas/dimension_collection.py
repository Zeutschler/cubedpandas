from typing import Iterable, Self
from hybrid_dict import HybridDict
import pandas as pd
from cubedpandas.dimension import Dimension


class DimensionCollection(Iterable[Dimension]):
    def __init__(self):
        self._dims: dict = {}
        self._counter: int = 0
        self._dims_list: list = []
        pass

    def __iter__(self) -> Self:
        self._counter = 0
        self._dims_list = list(self._dims.values())
        return self

    def __next__(self) -> Dimension:
        if self._counter >= len(self._dims):
            raise StopIteration
        dim = self._dims_list[self._counter]
        self._counter += 1
        return dim

    def __len__(self):
        return len(self._dims)

    def __getitem__(self, item) -> Dimension:
        return self._dims[item]

    def add(self, dimension: Dimension):
        self._dims[dimension.column] = dimension

