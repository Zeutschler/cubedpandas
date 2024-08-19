# CubedPandas - Copyright (c)2024 by Thomas Zeutschler, BSD 3-clause license, see LICENSE file.
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cubedpandas.slice.html_table import HtmlTable
    from slice.html_table import HtmlDesign


class Table:
    """Represents a table representing a slice. Base class for different implementations of a table."""

    def to_html(self, design:str = "simple", as_div: bool = False) -> str:
        """Returns the table either as a self-contained html page or
        as an HTML fragment to be placed inside an HTML `<div>` tag."""
        from cubedpandas.slice.html_table import HtmlTable
        return HtmlTable(design).to_html(as_div)


    def show(self) -> None:
        """Prints the table to the console."""


    def __str__(self) -> str:
        """Returns a string representation of the table."""
        pass
