# CubedPandas - Copyright (c)2024 by Thomas Zeutschler, BSD 3-clause license, see LICENSE file.

from __future__ import annotations
from typing import TYPE_CHECKING, Any

import pandas as pd

from cubedpandas.context.context import Context

from cubedpandas.slice.axis import Axis
from cubedpandas.slice.filters import Filters
from cubedpandas.slice.filter import Filter
from cubedpandas.slice.table_renderer import TableRenderer

# ___noinspection PyProtectedMember
if TYPE_CHECKING:
    from cubedpandas.cube import Cube
    from cubedpandas.measure_collection import MeasureCollection
    from cubedpandas.measure import Measure
    from cubedpandas.dimension import Dimension
    from cubedpandas.dimension_collection import DimensionCollection



class Slice:
    """A slice represents a view on a cube, and allows for easy access to the underlying Pandas dataframe.
    Typically, a slice has rows, columns and filter, just like in an Excel PivotTable. Slices
    are easy to define and use for convenient data analysis."""

    def __init__(self, context: Context | 'Cube', rows: Any = None, columns: Any = None,
                 filters: Any = None, config: dict | str | None = None):
        """
        Creates a slice upon a cube or cube-context. A slice is a view on a cube, and allows for easy access
        to data in tabular form. Slices can be configured to create simple to complex views on the underlying cube.

        Args:
            context:
                A context or cube object that defines the underlying data source for the slice. If a context is
                provided, the filters of the slice will refer to the context. If a cube is provided, no filters
                will be applied.

            rows:
                (optional) Either a context or any valid expression that could be used define or resolve
                the rows to be displayed in the slice. Default value is `None`.

            columns:
                (optional) Either a context or any valid expression that could be used define or resolve
                the columns to be displayed in the slice. Default value is `None`.

            filters:
                (optional) Either a context or any valid expression that could be used define or resolve
                one or multpile filters to be applied and displayed in the slice. Default value is `None`.

            config:
                (optional) A dictionary object, JSON string or a reference to a filename containing a
                valid configuration for the slice. Please refer to the documentation for more information
                on the configuration options for slices.
                Default value is `None`.

        Returns:
            A new Slice object for data navigation and tabular data visualization.

        Raises:
            ValueError:
                If the values for the paramerters rows, columns, filters or config are invalid.

        Examples:
            >>> df = pd.value([{"product": ["A", "B", "C"]}, {"value": [1, 2, 3]}])
            >>> cdf = cubed(df)
            >>> Slice(cdf,"product").print()
            +---+-------+
            |   | value |
            +---+-------+
            | A |     1 |
            | B |     2 |
            | C |     3 |
            +---+-------+
        """
        # input parameters
        from cubedpandas.cube import Cube
        if isinstance(context, Cube):
            self._cube: Cube = context
            self._context: Context | None = None
        else:
            self._cube: Cube = context.cube
            self._context: Context = context
        self._rows = rows
        self._columns = columns
        self._slice_filters = filters
        self._config = config

        # slice configuration
        self._axis: dict[str, Axis]  = {}
        self._filters: Filters = Filters()

        # initial slice validation and refresh
        self._is_prepared: bool = self._prepare()  # will raise an error if the slice is not valid
        self._is_refreshed: bool = self._refresh()  # will raise an error if the slice cannot be refreshed


    # region Public properties
    @property
    def rows(self) -> Axis | None:
        """Returns the rows of the slice."""
        return self._axis.get("rows", None)

    @property
    def columns(self) -> Axis | None:
        """Gets or sets the rows for the slice."""
        return self._axis.get("columns", None)

    @property
    def has_rows(self) -> bool:
        """Returns True if the slice has rows defined."""
        return self._rows is not None

    @property
    def has_columns(self) -> bool:
        """Returns True if the slice has columns defined."""
        return self._columns is not None

    @property
    def filters(self) -> Filters:
        """Gets or sets the filters for the slice."""
        return self._slice_filters

    #endregion

    # region Public methods
    def refresh(self) -> bool:
        """Refreshes the slice based on the current configuration and data from the underlying cube and dataframe."""
        if not self._is_prepared:
            self._prepare()
        return self._refresh()

    def show(self):
        """Prints the slice to the console."""
        print(self.__str__())

    def to_html(self, design: str = "simple", as_div: bool = False) -> str:
        """Returns the slice as an HTML table."""
        table = TableRenderer.render(self)
        return table.to_html(design, as_div)
    #endregion

    #region Magic methods
    def __str__(self):
        table = TableRenderer.render(self)
        return table.__str__()

    def __repr__(self):
        if self._context is not None:
            return f"{self.__class__.__name__}[{self._context}]"
        else:
            return f"{self.__class__.__name__}[cube]"

    #region Internal methods
    def _prepare(self) -> bool:
        """Validates the slice definition and prepares the slice for data retrieval through the `refresh()`method."""

        # 1. setup filters based on the context
        self._prepare_filters()

        # 2. check and prepare rows and columns
        if self.has_rows and (not self.has_columns):
            self._prepare_axis("rows", self._rows),
            # no columns defined, so we use all available measures as columns, if possible.
            if not self._axis["rows"].contains_any((Measure, MeasureCollection)):
                self._columns = self._cube.measures
                self._prepare_axis("columns", self._columns)

        elif (not self.has_rows) and self.has_columns:
            self._prepare_axis("columns", self._columns)
            # no rows defined, so we use all available measures as columns, if possible.
            if not self._axis["columns"].contains_any((Measure, MeasureCollection)):
                self._columns = self._cube.measures
                self._prepare_axis("rows", self._columns)

        elif (not self.has_rows) and (not self.has_columns):
            # The slice must was called without any rows or columns definitions
            # Let's create a default slice with the first dimension as rows and all available measures as columns
            if len(self._cube.dimensions) > 0:
                self._rows = self._cube.dimensions[0]
                self._prepare_axis("rows", self._rows)
                if len(self._cube.measures) > 0:
                    self._columns = self._cube.measures
                    self._prepare_axis("columns", self._columns)
                else:
                    # No measures available in the cube, so we just count the rows
                    self._prepare_axis("columns", "count")
            else:
                # No dimensions available in the cube, so we use all measures as columns
                if len(self._cube.measures) > 0 :
                    self._rows = "*"   # filter for all rows
                    self._prepare_axis("rows", self._rows)
                    self._columns = self._cube.measures
                    self._prepare_axis("columns", self._columns),
        else:
            self._prepare_axis("rows", self._rows)
            self._prepare_axis("columns", self._columns)

        return True


    def _prepare_filters(self):
        """Prepares the filters for the slice based on the context."""
        if self._context is None:
            return # nothing to do here

        # deserialize chain of context objects into a list filter objects
        context = self._context
        while context is not None:
            filter = Filter(context)
            self._filters.append(filter)
            context = context.parent
        # reverse the list of filters, so we have the innermost filter on top of the filters.
        self._filters.reverse()

        # add additional filters defined
        if self._slice_filters is not None:
            if isinstance(self._slice_filters, (tuple, list)):
                for context in self._slice_filters:
                    filter = Filter(context)
                    self._filters.append(filter)
            else:
                filter = Filter(self._slice_filters)
                self._filters.append(filter)


    def _prepare_axis(self, axis_name: str, axis_definition: Any | None):
        """Prepares an axis for the slice."""
        if axis_definition is None:
            raise ValueError(f"Axis '{axis_name}' is not defined by axis-definition '{axis_definition}'.")

        axis = Axis(name=axis_name, data=axis_definition)
        self._axis[axis_name] = axis

    def _refresh(self) -> bool:
        """Refreshes the slice based on the current configuration and data from the underlying cube and dataframe."""
        if not self._is_prepared:
            return False

        from cubedpandas.measure_collection import MeasureCollection
        from cubedpandas.measure import Measure
        from cubedpandas.dimension import Dimension
        from cubedpandas.dimension_collection import DimensionCollection

        # todo: DUMMY implementation only...
        # evaluate all available rows and columns blocks (just one for now)
        # 1. get the row mask from the filters
        if self.filters is not None:
            row_mask = self.filters.row_mask()
            df = self._cube._df[row_mask]
        else:
            df = self._cube._df

        # 2. get the data from the cube (for now, we assume that both axes have only one block)
        row_item = self._axis["rows"].blocks[0].block_sets[0].item
        # for now, we assume just Dimensions on the row
        if isinstance(row_item, Dimension):
            row_item = [row_item,]
        elif isinstance(row_item, DimensionCollection):
            row_item = [dim for dim in row_item]
        elif isinstance(row_item, (list[Dimension], tuple[Dimension])):
            pass
        else:
            raise ValueError(f"Invalid row item type '{type(row_item)}'.")
        column_item = self._axis["columns"].blocks[0].block_sets[0].item  # for now, we assume some Measures

        # Now lets use a pivottable to generate the output
        #   see: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.pivot_table.html
        values = [measure.column for measure in column_item]
        index = [item.column for item in row_item]  # dimension column, also nested supported ['A', 'B']
        aggfunc = {}
        for measure in column_item:
            aggfunc[measure.column] = "sum"

        result = pd.pivot_table(df, values=values, index=index, aggfunc=aggfunc)

        # table = pd.pivot_table(df, values=['Amount'],
        #                        index=['Location', 'Employee'],
        #                        columns=['Account', 'Currency'],
        #                        fill_value=0, aggfunc=np.sum, dropna=True, )
        #
        # for subtotals see: https://stackoverflow.com/questions/41383302/pivot-table-subtotals-in-pandas
        # pd.concat([
        #     d.append(d.sum().rename((k, 'Total')))
        #     for k, d in table.groupby(level=0)
        # ]).append(table.sum().rename(('Grand', 'Total')))
        #
        #
        #                   Amount
        # Account            Basic         Net
        # Currency             GBP   USD   GBP   USD
        # Location Employee
        # Airport  2             0  3000     0  2000
        #          Total         0  3000     0  2000
        # Town     1             0  4000     0  3000
        #          3          5000     0  4000     0
        #          Total      5000  4000  4000  3000
        # Grand    Total      5000  7000  4000  5000

        print(result)
        return True
    #endregion

