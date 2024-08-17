from __future__ import annotations
from typing import TYPE_CHECKING, Any, TypeVar, Tuple
from enum import IntEnum
import numpy as np
from cubedpandas.context.context import Context

if TYPE_CHECKING:
    from cubedpandas.cube import Cube
    from cubedpandas.context.context import MemberContext


class BooleanOperationContextEnum(IntEnum):
    AND = 1
    OR = 2
    XOR = 3
    NOT = 4


class BooleanOperationContext(Context):
    """ A context representing a boolean operation between two Context objects."""

    def __init__(self, left: Context, right: Context | None = None,
                 operation: BooleanOperationContextEnum = BooleanOperationContextEnum.AND):
        self._left: Context = left
        self._right: Context | None = right
        self._operation: BooleanOperationContextEnum = operation
        match self._operation:
            case BooleanOperationContextEnum.AND:
                row_mask = np.intersect1d(left.row_mask, right.row_mask, assume_unique=True)
            case BooleanOperationContextEnum.OR:
                row_mask = np.union1d(left.row_mask, right.row_mask)
            case BooleanOperationContextEnum.XOR:
                row_mask = np.setxor1d(left.row_mask, right.row_mask, assume_unique=True)
            case BooleanOperationContextEnum.NOT:
                row_mask = np.setdiff1d(left._df.index.to_numpy(), left.row_mask, assume_unique=True)
            case _:
                raise ValueError(f"Invalid boolean operation '{operation}'. Only 'AND', 'OR' and 'XOR' are supported.")

        if self._operation == BooleanOperationContextEnum.NOT:
            # unary operation
            super().__init__(cube=left.cube, address=None, parent=left.parent,
                             row_mask=row_mask, member_mask=None,
                             measure=left.measure, dimension=left.dimension, resolve=False)
        else:
            # binary operations
            super().__init__(cube=right.cube, address=None, parent=left.parent,
                             row_mask=row_mask, member_mask=None,
                             measure=right.measure, dimension=right.dimension, resolve=False)

        @property
        def left(self) -> Context:
            return self._left

        @property
        def right(self) -> Context | None:
            return self._right

        @property
        def operation(self) -> BooleanOperationContextEnum:
            return self._operation