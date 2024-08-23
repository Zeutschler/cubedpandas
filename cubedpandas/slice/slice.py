# CubedPandas - Copyright (c)2024, Thomas Zeutschler, see LICENSE file

from __future__ import annotations
from typing import TYPE_CHECKING, Any
import pandas as pd

from cubedpandas.context.context import Context
from cubedpandas.slice.axis import Axis
from cubedpandas.slice.filters import Filters
from cubedpandas.slice.filter import Filter

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
                 config: dict | str | None = None):
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
        self._config = config
        self._pivot_table: pd.DataFrame = None
        self._axis: dict[str, Axis] = {}
        self._filters: Filters = Filters()

        # initial slice validation and refresh
        self._output: str = None
        self._is_prepared: bool = self._prepare()  # will raise an error if the slice is not valid
        self._is_refreshed: bool = self._refresh()  # will raise an error if the slice cannot be refreshed

    # region Public properties
    @property
    def cube(self) -> 'Cube':
        """Returns the cube the slice refers to."""
        return self._cube

    @property
    def filters(self) -> Filters:
        """Returns the filters of the slice."""
        return self._filters

    @property
    def rows(self) -> Axis | None:
        """Returns the rows of the slice."""
        return self._axis.get("rows", None)

    @property
    def columns(self) -> Axis | None:
        """Returns the columns of the slice."""
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
    def has_filters(self) -> bool:
        """Returns True if the slice has filters defined."""
        return len(self._filters) > 0

    @property
    def pivot_table(self) -> pd.DataFrame | None:
        """Returns the Pandas dataframe/pivot-table representing the slice."""
        return self._pivot_table

    # endregion

    # region Public methods
    def refresh(self) -> bool:
        """Refreshes the slice based on the current configuration and data from the underlying cube and dataframe."""
        if not self._is_prepared:
            self._prepare()
        return self._refresh()

    def show(self):
        """Prints the slice to the console."""
        print(self._pivot_table)

    def to_html(self, classes: str | list | tuple | None = None, style:str= None) -> str | None:
        """Returns the slice as an HTML table."""
        if self._pivot_table is None:
            return None
        html = self._pivot_table.to_html(classes=classes, float_format=self._float_formatter, justify="justify-all")
        if style is not None:
            html = html.replace("<table", f"<table style='{style}'")
        return html

    @staticmethod
    def _float_formatter(x: float) -> str:
        """Formats a float value."""
        return f"{x:,.2f}"

    # endregion

    # region Magic methods
    def __str__(self):
        return f"{self._pivot_table.__str__()}"

    def __repr__(self):
        if self._cube._runs_in_jupyter:
            from IPython.display import display
            display(self._pivot_table)
            return ""
        else:
            return f"{self._pivot_table.__repr__()}"


    # region Internal methods
    def _prepare(self) -> bool:
        """Validates the slice definition and prepares the slice for data retrieval through the `refresh()`method."""

        from cubedpandas.measure_collection import MeasureCollection
        from cubedpandas.measure import Measure

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
                if len(self._cube.measures) > 0:
                    self._rows = "*"  # filter for all rows
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
            return  # nothing to do here

        # deserialize chain of context objects into a list filter objects
        context = self._context
        while context is not None:
            filter = Filter(context)
            self._filters.append(filter)
            context = context.parent
        # reverse the list of filters, so we have the innermost filter on top of the filters.
        self._filters.reverse()

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
        from cubedpandas.context.dimension_context import DimensionContext

        # todo: DUMMY implementation only...
        # evaluate all available rows and columns blocks (just one for now)
        # 1. get the row mask from the filters
        df = self._cube._df
        row_mask = self.filters.row_mask()
        if row_mask is not None:
            df = df.iloc[row_mask]

        # 2. get the data from the cube (for now, we assume that both axes have only one block)
        measures = [measure for measure in self._cube.measures]
        row_items = [item.item for item in self._axis["rows"].blocks[0].block_items.to_list()]
        # for now, we assume just Dimensions on the row
        for item in row_items:
            if isinstance(item, DimensionCollection):
                row_items = [dim for dim in row_items]
                break
            elif isinstance(item, Dimension):
                pass
            elif isinstance(item, Measure):
                measures = [item, ]
            elif isinstance(item, MeasureCollection):
                measures = [measure for measure in item]
            elif not isinstance(item, (DimensionContext, Dimension)):
                raise ValueError(f"Invalid row item type '{type(item.item)}'.")

        column_items = [item.item for item in self._axis["columns"].blocks[0].block_items.to_list()]
        for item in column_items:
            if isinstance(item, DimensionCollection):
                column_items = [dim for dim in row_items]
                break
            elif isinstance(item, Measure):
                measures = [item, ]
            elif isinstance(item, MeasureCollection):
                measures = [measure for measure in item]
                column_items = []
                break
            elif not isinstance(item, (DimensionContext, Dimension)):
                raise ValueError(f"Invalid row item type '{type(item.item)}'.")

        # Create a Pandas pivot table to generate the desired output
        values = [m.column for m in measures]
        aggfunc = {}
        for measure in values:
            aggfunc[measure] = "sum"

        index = [item.column if isinstance(item, Dimension) else item.dimension.column for item in row_items]
        columns = [item.column for item in column_items]

        pvt = pd.pivot_table(df, values=values, index=index, columns=columns, aggfunc=aggfunc,
                             fill_value=0, dropna=True, margins=False, margins_name='(all)')

        # subtotal of the rows
        row_items_count = len(row_items)
        if row_items_count > 1:
            subtotal_rows = pvt.groupby(level=0).sum()
            # rename the index in order to concatenate  with pvt
            subtotal_rows.index = pd.MultiIndex.from_tuples([(item, '(all)', "") for item in subtotal_rows.index])
            # add the subtotals rows to pvt
            pvt = pd.concat([pvt, subtotal_rows], join="outer").sort_index()

            # index = pvt.index
            # names = pvt.index.names
            # new_names = ["#ordinal",].extend(names)
            # new_tuples = [tuple([r*10]) + item for r, item in enumerate(index)]
            # new_index = pd.MultiIndex.from_tuples(new_tuples, names=new_names)
            #
            # pvt.set_index(new_index, inplace=True)
            #
            # for level in range(1, row_items_count):
            #
            #     subtotal_rows = pvt.groupby(level=level).sum()
            #     values = subtotal_rows.index.values.tolist()
            #     pvt.index.searchsorted() .searchsorted('a', side='right')
            #
            #     sub_total_tuples = [(t[0]) + (t[level]) for t in new_tuples if (t[level] in values) ]
            #
            #     # rename the index in order to concatenate  with pvt
            #     subtotal_label = ["" for i in range(row_items_count + 1)]
            #     subtotal_tuples = []
            #     for item in subtotal_rows.index:
            #         subtotal_label[level] = item
            #         subtotal_label[level + 1] = "(all)"
            #         subtotal_tuples.append(tuple(subtotal_label))
            #     subtotal_rows.index = pd.MultiIndex.from_tuples(subtotal_tuples)
            #
            #     # add the subtotals rows to pvt
            #     df = pd.concat([pvt, subtotal_rows], join="outer")
            #
            # pvt = df.sort_index(level=0)

        if False:
            # subtotal of the columns
            subtotal_cols = pvt.sum(level=1, axis=1)

            # rename the columns in order to join with pvt
            subtotal_cols.columns = pd.MultiIndex.from_arrays(
                [len(subtotal_cols.columns) * ["ID"], subtotal_cols.columns,
                 len(subtotal_cols.columns) * ['subtotal']])

            # add the subtotals columns to pvt
            pvt = pvt.join(subtotal_cols).sort_index(axis=1)

            # Add the totals of the columns and rows
            # Divide by 2 because we are summing the subtotals rows and columns too
            pvt.loc[("Total", ""), :] = pvt.sum() / 2
            pvt.loc[:, ("ID", "Total", "")] = pvt.sum(axis=1) / 2

        # apply formatting
        df.style \
            .format(precision=2, thousands=".", decimal=",") \
            .format_index(str.upper, axis=1)

        # return result
        self._pivot_table = pvt
        return True

    # endregion
