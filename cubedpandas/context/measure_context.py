from __future__ import annotations
from typing import TYPE_CHECKING, Any

from cubedpandas.context.context import Context

if TYPE_CHECKING:
    from cubedpandas.cube import Cube
    from cubedpandas.measure import Measure
    from cubedpandas.dimension import Dimension

class MeasureContext(Context):
    """
    A context representing a measure of the cube.
    """

    def __init__(self, cube: Cube, parent: Context | None, address: Any = None, row_mask: np.ndarray | None = None,
                 measure: Measure | None = None, dimension: Dimension | None = None, resolve: bool = True,
                 filtered: bool = False):
        self._filtered: bool = filtered
        super().__init__(cube=cube, address=address, parent=parent, row_mask=row_mask,
                         measure=measure, dimension=dimension, resolve=resolve, filtered=filtered)
