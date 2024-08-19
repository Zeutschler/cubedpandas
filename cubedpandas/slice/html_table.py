# CubedPandas - Copyright (c)2024 by Thomas Zeutschler, BSD 3-clause license, see LICENSE file.
from abc import abstractproperty, abstractmethod

from cubedpandas.slice.table import Table

class HtmlTable(Table):
    """A table representing a slice that can be rendered as an HTML table."""

    def __init__(self, design:str | None = "material"):
        """
        Initializes the HTML table.
        Args:
            design: The design to be used to render the HTML table.
                If the requested design does not exist or is `None`,
                then the default design "simple" will be returned.

                Currently, the following designs are supported:
                - "simple": Plain simple HTML (https://www.w3schools.com/html/html_tables.asp).
                - "material": Google's Material design (https://m3.material.io).

        """
        design, html_design = HtmlDesignFactory.get_design(design=design)
        self._design: str = design
        self._html_design: HtmlDesign = html_design

    #region Public properties
    @property
    def design(self) -> str:
        """Returns the design of the HTML table."""
        return self._design

    @design.setter
    def design(self, value:str):
        """Sets the design of the HTML table."""
        design, html_design = HtmlDesignFactory.get_design(design=design)
        self._design: str = design
        self._html_design: HtmlDesign = html_design

    def to_html(self, as_div:bool = False) -> str:
        """Returns the table either as a self-contained html page or
        as an HTML fragment to be placed inside an HTML `<div>` tag."""
        if as_div:
            return self._html_design.html(full_page_html=False)
        else:
            return self._html_design.html(full_page_html=False)
    #endregion

    def __str__(self):
        return self.html


class HtmlDesign:
    """Base class for HTML table designs."""
    pass

    @property
    def design_weblink(self) -> str:
        """Returns a weblink to the design homepage."""
        return "https://www.w3schools.com/html/html_tables.asp"

    def html(self, full_page_html: bool = True) -> str:
        """Renders the HTML table."""
        return "HtmlDesign"


class HtmlDesignFactory:
    """Factory for creating HTML table styles."""
    @staticmethod
    def get_design(self, design:str) -> HtmlDesign:
        """
        Returns a design for the HTML table output of a slice.

        """
        if design is None:
            design = "simple"
        if not isinstance(design, str):
            design = str(design)
        design = design.lower().strip()

        match design:
            case "material":
                return HtmlDesignMaterial()
            case _:
                return HtmlDesignSimple()


class HtmlDesignSimple(HtmlDesign):
    """A Styles for an HTML table."""

    @property
    def design_weblink(self) -> str:
        """Returns a weblink to the design homepage."""
        return "https://www.w3schools.com/html/html_tables.asp"

    def html(self, full_page_html: bool = True) -> str:
        """Renders the HTML table."""
        return "HtmlDesign"


class HtmlDesignMaterial(HtmlDesign):
    """Material design for an HTML table."""

    @property
    def design_weblink(self) -> str:
        """Returns a weblink to the design homepage."""
        return "https://m3.material.io"

    def html(self, full_page_html: bool = True) -> str:
        """Renders the HTML table."""
        return "HtmlDesign"
