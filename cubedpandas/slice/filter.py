# CubedPandas - Copyright (c)2024 by Thomas Zeutschler, BSD 3-clause license, see LICENSE file.

from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from cubedpandas import Dimension, Measure, Cube, Member
    from cubedpandas.context import (Context, FilterContext, MemberContext, MeasureContext, DimensionContext,
                                     CubeContext, BooleanOperationContext, BooleanOperationContextEnum,
                                     CompoundContext, MemberNotFoundContext)


class Filter:
    """
    Defines a filter of a slice. Either a single measure or a set of dimension members from one dimension.

    A slice consists of 2 axes, rows and columns. Each axis is divided into 0 to N blocks,
    which by themselves are defined by 1 to M sets of dimension members and/or measures.
    Block are independent of each other and can contain and reference different members
    from different dimensions or measures.
    """
    def __init__(self, context: 'Context' | Any):
        self._context: 'Context' = context

    @property
    def context(self) -> 'Context':
        return self._context
