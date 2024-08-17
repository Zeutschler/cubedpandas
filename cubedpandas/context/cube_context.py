# CubedPandas - Copyright (c)2024 by Thomas Zeutschler, BSD 3-clause license, see LICENSE file.

from __future__ import annotations
from typing import TYPE_CHECKING

from cubedpandas.context.context import Context

if TYPE_CHECKING:
    from cubedpandas.cube import Cube


class CubeContext(Context):
    """
    A context representing the cube itself.
    """

    def __init__(self, cube: 'Cube', dynamic_attribute: bool = False):
        super().__init__(cube=cube, address=None, parent=None, row_mask=None, measure=None,
                         dynamic_attribute=dynamic_attribute)
        self._measure = cube.measures.default
