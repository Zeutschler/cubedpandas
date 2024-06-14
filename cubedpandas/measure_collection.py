# measure_collection.py
# CubedPandas - Multi-dimensional data analysis for Pandas dataframes.
# ©2024 by Thomas Zeutschler. All rights reserved.
# MIT License - please see the LICENSE file that should have been included in this package.

from typing import Iterable, Self
from cubedpandas.measure import Measure


class MeasureCollection(Iterable[Measure]):
    """
    Represents the available/defined Measures of a Cube.
    """

    def __init__(self):
        self._measures: dict = {}
        self._counter: int = 0
        self._measure_list: list = []
        pass

    def __iter__(self) -> Self:
        self._counter = 0
        self._measure_list = list(self._measures.values())
        return self

    def __next__(self) -> Measure:
        if self._counter >= len(self._measures):
            raise StopIteration
        dim = self._measure_list[self._counter]
        self._counter += 1
        return dim

    def __len__(self):
        return len(self._measures)

    def __getitem__(self, item) -> Measure:
        if isinstance(item, str):
            return self._measures[item]
        return self._measure_list[item]

    def __contains__(self, item) -> bool:
        return item in self._measures

    def add(self, measure: Measure):
        self._measures[measure.column] = measure
        self._measure_list = list(self._measures.values())

