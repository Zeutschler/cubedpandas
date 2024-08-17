from __future__ import annotations
from typing import TYPE_CHECKING, Any, TypeVar, Tuple

from cubedpandas.context.context import Context

if TYPE_CHECKING:
    from cubedpandas.cube import Cube
    from cubedpandas.context.context import MemberContext


class CubeContext(Context):
    """
    A context representing the cube itself.
    """

    def __init__(self, cube: 'Cube'):
        super().__init__(cube=cube, address=None, parent=None, row_mask=None, measure=None)
        self._measure = cube.measures.default