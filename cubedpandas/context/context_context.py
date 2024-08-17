from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from cubedpandas.context.context import Context

if TYPE_CHECKING:
    from cubedpandas.context.filter_context import FilterContext


class ContextContext(Context):
    """
    A context representing by an existing context
    """

    def __init__(self, parent: Context, nested: Context):
        from cubedpandas.context.filter_context import FilterContext

        # merge the row masks of the parent and the nested context, e.g. parent[nested]
        if parent.dimension == nested.dimension:
            parent_row_mask = parent.get_row_mask(before_dimension=parent.dimension)
            member_mask = np.union1d(parent.member_mask, nested.member_mask)
            if parent_row_mask is None:
                row_mask = member_mask
            else:
                row_mask = np.intersect1d(parent_row_mask, member_mask, assume_unique=True)

        elif isinstance(nested.parent, FilterContext):
            if parent.row_mask is None:
                row_mask = nested.row_mask
            elif nested.row_mask is None:
                row_mask = parent.row_mask
            else:
                row_mask = np.intersect1d(parent.row_mask, nested.row_mask, assume_unique=True)

        else:
            member_mask = nested.member_mask
            if parent.row_mask is None:
                row_mask = nested.row_mask
            else:
                row_mask = np.intersect1d(parent.row_mask, member_mask, assume_unique=True)

        super().__init__(cube=parent.cube, address=nested.address, parent=parent,
                         row_mask=row_mask, member_mask=nested.member_mask,
                         measure=nested.measure, dimension=nested.dimension,
                         resolve=False)
        self._referenced_context = nested

    @property
    def referenced_context(self):
        return self._referenced_context