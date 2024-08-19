# CubedPandas - Copyright (c)2024 by Thomas Zeutschler, BSD 3-clause license, see LICENSE file.
from collections import namedtuple

from cubedpandas.slice.table import Table

class TextTable(Table):
    """A table representing a slice that can be rendered as a text table using monospaced fonts."""
    pass
    Line = namedtuple("Line", ["begin", "hline", "sep", "end"])
    DataRow = namedtuple("DataRow", ["begin", "sep", "end"])
    TableFormat = namedtuple(
        "TableFormat",
        [
            "top_line",
            "sep_line",
            "end_line",
            "row",
            "padding",
        ],
    )
    _table_formats = {
        "simple": TableFormat(
        top_line=Line("┌", "─", "┬", "┐"),
        sep_line=Line("├", "─", "┼", "┤"),
        end_line=Line("└", "─", "┴", "┘"),
        row=DataRow("│", "│", "│"),
        padding=1
    )}

    def __init__(self):
        """Initializes the text table."""
        pass

# Sample Table layout from DuckDB
# ┌──────────────────┬──────────────────┬─────────────────────┬──────────────┬────────────┬─────────┐
# │      Alias       │      Kunde       │      Standort       │  Sensorname  │   Datum    │ Besuche │
# │     varchar      │     varchar      │       varchar       │   varchar    │    date    │  int64  │
# ├──────────────────┼──────────────────┼─────────────────────┼──────────────┼────────────┼─────────┤
# │ 10436-002_1.U1_2 │ Lindenplatz Nord │ Columbia Sportswear │ Ein-/Ausgang │ 2023-11-24 │    4703 │
# │ 10436-002_1.U1_2 │ Lindenplatz Nord │ Columbia Sportswear │ Ein-/Ausgang │ 2023-11-25 │    3853 │
# │ 10436-002_1.U1_2 │ Lindenplatz Nord │ Columbia Sportswear │ Ein-/Ausgang │ 2023-11-18 │    3471 │
# │ 10436-002_1.U1_2 │ Lindenplatz Nord │ Columbia Sportswear │ Ein-/Ausgang │ 2023-12-27 │    2848 │
# │ 10436-002_1.U1_2 │ Lindenplatz Nord │ Columbia Sportswear │ Ein-/Ausgang │ 2023-10-21 │    2735 │
# └──────────────────┴──────────────────┴─────────────────────┴──────────────┴────────────┴─────────┘