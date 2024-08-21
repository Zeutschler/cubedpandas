# CubedPandas - Copyright (c)2024, Thomas Zeutschler, see LICENSE file

from enum_tools import IntEnum

from cubedpandas.slice.slice import Slice
from cubedpandas.slice.table import Table
from cubedpandas.slice.html_table import HtmlTable
from cubedpandas.slice.text_table import TextTable

class RenderTargetEnum(IntEnum):
    """Enum for render targets."""
    HTML = 1
    TEXT = 2

class Renderer:
    """Renders a slice as a table."""

    pass

    @staticmethod
    def render(slice:Slice, target:RenderTargetEnum = RenderTargetEnum.TEXT) -> Table:
        """Renders a table from a slice."""
        pass
