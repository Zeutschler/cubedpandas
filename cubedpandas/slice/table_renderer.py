from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from cubedpandas.slice.slice import Slice
    from cubedpandas.slice.table import Table

class TableRenderer:
    """Renders and converts a slice into a generic Table object,
    which then can be converted into an HTML or text table."""

    @staticmethod
    def render(slice: 'Slice') -> 'Table':
        from cubedpandas.slice.table import Table
        table = Table()

        return table