# CubedPandas - Copyright (c)2024, Thomas Zeutschler, see LICENSE file

from __future__ import annotations
from typing import TYPE_CHECKING, Any
import numpy as np

from cubedpandas.context.context import Context

if TYPE_CHECKING:
    from cubedpandas.cube import Cube
    from cubedpandas.measure import Measure
    from cubedpandas.dimension import Dimension
    from cubedpandas.context.member_context import MemberContext


class DimensionContext(Context):
    """
    A context representing a dimension of the cube.
    """

    def __init__(self, cube: Cube, parent: Context | None, address: Any = None, row_mask: np.ndarray | None = None,
                 measure: Measure | None = None, dimension: Dimension | None = None, resolve: bool = True):
        super().__init__(cube=cube, address=address, parent=parent, row_mask=row_mask,
                         measure=measure, dimension=dimension, resolve=resolve)

        if cube.settings.populate_members:
            # Support for dynamic attributes
            for member in dimension.members:
                member = member.replace(" ", "_")
                if member not in self.__dict__:
                    from cubedpandas.context.context_resolver import ContextResolver
                    member_context = ContextResolver.resolve(parent=self, address=member,
                                                             dynamic_attribute=True, target_dimension=dimension)
                    setattr(self, member, member_context)

    @property
    def members(self) -> list:
        return self._dimension.members
