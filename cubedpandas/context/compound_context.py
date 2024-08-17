from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cubedpandas.context.context import Context

if TYPE_CHECKING:
    from cubedpandas.context.member_context import MemberContext

class CompoundContext(Context):
    def __init__(self, parent:Context, rows: Any, columns: Any | None = None):
        super().__init__(cube = parent.cube, parent=parent, address = parent.address,
                        row_mask=parent.row_mask, member_mask=parent.member_mask, measure=parent.measure,
                        dimension = parent.dimension, resolve=False)
        self._parent:Context = parent
        self.rows = rows
        self.columns = columns

    def get(self, key) -> Context  | (Any, Any):
        from cubedpandas.context.member_context import MemberContext

        if isinstance(self._parent, MemberContext):
            return self._parent

        return self._rows, self._columns