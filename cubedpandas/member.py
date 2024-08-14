from typing import SupportsFloat, TYPE_CHECKING, Any
from cubedpandas.dimension import Dimension
import numpy as np


class Member:
    def __init__(self, dimension: Dimension, name):
        self.name:str = name
        self.alias:str | None = None
        self.dimension:Dimension = dimension
        self._row_mask: np.ndarray | None = None

    @property
    def row_mask(self) -> np.ndarray | None:
        return self._row_mask
    @row_mask.setter
    def row_mask(self, value: np.ndarray):
        self._row_mask = value

    def __repr__(self):
        return str(self.name)


class MemberSet(set):
    def __init__(self, dimension:Dimension, address:Any, row_mask: np.ndarray| None, members = ()):
        super().__init__(members)
        self._dimension: Dimension = dimension
        self._address = address
        self._members = members
        self._row_mask: np.ndarray | None = row_mask
        # self.add(Member(dimension, address))

    @property
    def address(self):
        return self._address

    @property
    def row_mask(self):
        return self._row_mask
