# CubedPandas - Copyright (c)2024 by Thomas Zeutschler, BSD 3-clause license, see file LICENSE included in this package.

import sys
import builtins
from typing import Type
from types import ModuleType, FunctionType
from gc import get_referents
from typing import Any, List, Tuple
from datetime import datetime
import numpy as np
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype as is_datetime
from pandas.api.types import (is_numeric_dtype, is_string_dtype, is_bool_dtype,
                              is_categorical_dtype, is_object_dtype, is_timedelta64_dtype,
                              is_period_dtype, is_interval_dtype, is_complex_dtype,
                              is_integer_dtype, is_float_dtype)


from cubedpandas.cube_aggregation import CubeAggregationFunctionType, CubeAggregationFunction, CubeAllocationFunctionType
from cubedpandas.schema import Schema
from cubedpandas.measure_collection import MeasureCollection
from cubedpandas.measure import Measure
from cubedpandas.dimension_collection import DimensionCollection
from cubedpandas.dimension import Dimension
from cubedpandas.ambiguities import Ambiguities
from cubedpandas.filter import Filter, FilterOperation
from cubedpandas.caching_strategy import CachingStrategy, EAGER_CACHING_THRESHOLD
from cubedpandas.cell import Cell
from cubedpandas.slice import Slice


class Cube:
    """
    Wraps a Pandas dataframes into a cube to provide convenient multi-dimensional access
    to the underlying dataframe for easy aggregation, filtering, slicing, reporting and
    data manipulation and write back.
    A schema, that defines the dimensions and measures of the Cube, can either be
    inferred automatically from the underlying dataframe (default) or defined explicitly.
    """

    def __init__(self, df: pd.DataFrame, schema=None,
                 infer_schema: bool = True,
                 caching: CachingStrategy = CachingStrategy.LAZY,
                 caching_threshold: int = EAGER_CACHING_THRESHOLD,
                 read_only: bool = True,
                 ignore_key_errors: bool = True):
        """
        Wraps a Pandas dataframes into a cube to provide convenient multi-dimensional access
        to the underlying dataframe for easy aggregation, filtering, slicing, reporting and
        data manipulation and write back.

        Args:
            df:
                The Pandas dataframe to be wrapped into the CubedPandas `Cube` object.

            schema:
                (optional) A schema that defines the dimensions and measures of the Cube. If not provided, the schema will be inferred from the dataframe if
                parameter `infer_schema` is set to `True`. For further details please refer to the documentation of the
                `Schema` class.
                Default value is `None`.

            infer_schema:
                (optional) If no schema is provided and `infer_schema` is set to True, a suitable
                schema will be inferred from the unerlying dataframe. All numerical columns will
                be treated as measures, all other columns as dimensions. If this behaviour is not
                desired, a schema must be provided.
                Default value is `True`.

            caching:
                (optional) A caching strategy to be applied for accessing the cube. recommended
                value for almost all use cases is `CachingStrategy.LAZY`, which caches
                dimension members on first access. Caching can be beneficial for performance, but
                may also consume more memory. To cache all dimension members eagerly (on
                initialization of the cube), set this parameter to `CachingStrategy.EAGER`.
                Please refer to the documentation of 'CachingStrategy' for more information.
                Default value is `CachingStrategy.LAZY`.

            caching_threshold:
                (optional) The threshold as 'number of members' for EAGER caching only. If the number of
                distinct members in a dimension is below this threshold, the dimension will be cached
                eargerly, if caching is set to CacheStrategy.EAGER or CacheStrategy.FULL. Above this
                threshold, the dimension will be cached lazily.
                Default value is `EAGER_CACHING_THRESHOLD`, equivalent to 256 unique members per dimension.

            read_only:
                (optional) Defines if write backs to the underlying dataframe are permitted.
                If read_only is set to `True`, write back attempts will raise an `PermissionError`.
                If read_only is set to `False`, write backs are permitted and will be pushed back
                to the underlying dataframe.
                Default value is `True`.

            ignore_key_errors:
                (optional) If set to `True`, key errors for members of dimensions will be ignored and
                cell values will return 0.0 or `None` if no matching record exists. If set to `False`,
                key errors will be raised as exceptions when accessing cell values for non-existing members.
                Default value is `True`.

        Returns:
            A new Cube object that wraps the dataframe.

        Raises:
            PermissionError:
                If writeback is attempted on a read-only Cube.

            ValueError:
                If the schema is not valid or does not match the dataframe or if invalid
                dimension, member, measure or address agruments are provided.

        Examples:
            >>> df = pd.value([{"product": ["A", "B", "C"]}, {"value": [1, 2, 3]}])
            >>> cdf = cubed(df)
            >>> cdf["product:B"]
            2
        """
        self._convert_values_to_python_data_types: bool = True
        self._df: pd.DataFrame = df
        self._infer_schema: bool = infer_schema
        self._read_only: bool = read_only
        self._caching: CachingStrategy = caching
        self._caching_threshold: int = caching_threshold
        self._ignore_key_errors: bool = ignore_key_errors

        # get or prepare the cube schema and setup dimensions and measures
        if (schema is None) and infer_schema:
            schema = Schema(df).infer_schema()
        else:
            schema = Schema(df, schema, caching=caching)
        self._schema: Schema = schema
        self._dimensions: DimensionCollection = schema.dimensions
        self._measures: MeasureCollection = schema.measures
        self._ambiguities: Ambiguities | None = None

        # warm up cache, if required
        if self._caching >= CachingStrategy.EAGER:
            self._warm_up_cache()

        # setup default aggregation functions
        self._sum_op = CubeAggregationFunction(self, CubeAggregationFunctionType.SUM)
        self._avg_op = CubeAggregationFunction(self, CubeAggregationFunctionType.AVG)
        self._median_op = CubeAggregationFunction(self, CubeAggregationFunctionType.MEDIAN)
        self._min_op = CubeAggregationFunction(self, CubeAggregationFunctionType.MIN)
        self._max_op = CubeAggregationFunction(self, CubeAggregationFunctionType.MAX)
        self._count_op = CubeAggregationFunction(self, CubeAggregationFunctionType.COUNT)
        self._stddev_op = CubeAggregationFunction(self, CubeAggregationFunctionType.STD)
        self._var_op = CubeAggregationFunction(self, CubeAggregationFunctionType.VAR)
        self._pof_op = CubeAggregationFunction(self, CubeAggregationFunctionType.POF)
        self._nan_op = CubeAggregationFunction(self, CubeAggregationFunctionType.NAN)
        self._an_op = CubeAggregationFunction(self, CubeAggregationFunctionType.AN)
        self._zero_op = CubeAggregationFunction(self, CubeAggregationFunctionType.ZERO)
        self._nzero_op = CubeAggregationFunction(self, CubeAggregationFunctionType.NZERO)

    # region Properties
    @property
    def ambiguities(self) -> Ambiguities:
        """
        Returns:
            An Ambiguities object that provides information about ambiguous data types in the underlying dataframe.
        """
        if self._ambiguities is None:
            self._ambiguities = Ambiguities(self._df, self._dimensions, self._measures)
        return self._ambiguities

    @property
    def schema(self) -> Schema:
        """
        Returns:
            The Schema of the Cube which defines the dimensions and measures of the Cube.
        """
        return self._schema

    @property
    def df(self) -> pd.DataFrame:
        """Returns:
        The underlying Pandas dataframe of the Cube.
        """
        return self._df

    @property
    def dimensions(self) -> DimensionCollection:
        """
        Returns:
            The dimensions available through the Cube.
        """
        return self._schema.dimensions

    def __len__(self):
        """
        Returns:
            The number of records in the underlying dataframe of the Cube.
        """
        return len(self._df)

    @property
    def size_in_bytes(self) -> int:
        """
        Returns:
        The size in bytes allocated by the `Cube` object instance.
        The memory allocation by the underlying dataframe is not included.
        """
        df_memory = self._df.memory_usage(deep=True).sum()
        own_memory = self._getsize(self) - df_memory
        return df_memory + own_memory

    @staticmethod
    def _getsize(obj):
        """Returns the memory usage of an object in bytes."""
        blacklist = type, ModuleType, FunctionType, pd.DataFrame
        if isinstance(obj, blacklist):
            raise TypeError('getsize() does not take argument of type: ' + str(type(obj)))
        seen_ids = set()
        size = 0
        objects = [obj]
        while objects:
            need_referents = []
            for obj in objects:
                if not isinstance(obj, blacklist) and id(obj) not in seen_ids:
                    seen_ids.add(id(obj))
                    size += sys.getsizeof(obj)
                    need_referents.append(obj)
            objects = get_referents(*need_referents)
        return size

    def _warm_up_cache(self):
        """Warms up the cache of the Cube, if required."""
        if self._caching >= CachingStrategy.EAGER:
            for dimension in self._dimensions:
                dimension._cache_warm_up(caching_threshold=self._caching_threshold)

    def clear_cache(self):
        """
        Clears the cache of the Cube for all dimensions.
        """
        for dimension in self._dimensions:
            dimension.clear_cache()
    # endregion

    # region Data Access Methods
    def __getattr__(self, name) -> Cell | Filter:
        """
        Dynamically resolves dimensions, measure or member from the cube. This enables a more natural
        access to the cube data using the Python dot notation.

        Dimension or measure names (the columns of the underlying dataframe) are resolved first and
        need to be valid Python identifier/variable name. If a dimension with the given name
        is found, a Filter object is returned that can be used to filter the cube data.
        If a measure or member of a dimension is found, a Cell object is returned that represents
        the cube data/records related to the address.

        If the name is not a valid Python identifier (e.g. contains special characters), the `slicer`
        method needs to be used to resolve the name. e.g., `12 data%|` is a valid name for a column
        in a Pandas dataframe, but not a valid Python identifier/variable name, hence `cube["12 data%|"]`
        needs to be used to return the dimension, measure or column.

        Args:
            name: Name of a member or measure in the cube.

        Returns:
            A Cell object that represents the cube data related to the address.

        Samples:
            >>> cdf = cubed(df)
            >>> cdf.Online.Apple.cost
            50
        """

        # check for "as filter" usage of a measure, as indicated by the trailing "_" e.g. cdf.sales_ > 100
        if isinstance(name, str) and name.endswith("_"):
            measure_name = str(name)[:-1]
            if measure_name in self._measures:
                cell = Cell(self, address=measure_name, dynamic_access=True)
                from cubedpandas.filter import CellFilter
                return CellFilter(cell)

        # check if the name refers to a dimension
        if name in self._dimensions:
            # special case / convention:
            #   if a dimension is also a measure,
            #   the measure will be returned as a Cell.
            if name not in self._measures:
                return self._dimensions[name]

        return Cell(self, address=name, dynamic_access=True)

    def __getitem__(self, address: Any) -> Cell:
        """
        Returns a cell of the cube for a given address.
        Args:
            address:
                A valid cube address.
                Please refer the documentation for further details.

        Returns:
            A Cell object that represents the cube data related to the address.

        Raises:
            ValueError:
                If the address is not valid or can not be resolved.
        """
        return Cell(self, address=address)

    def __setitem__(self, address, value):
        """
        Sets a value for a given address in the cube.
        Args:
            address:
                A valid cube address.
                Please refer the documentation for further details.
            value:
                The value to be set for the data represented by the address.
        Raises:
            PermissionError:
                If write back is attempted on a read-only Cube.
        """
        if self._read_only:
            raise PermissionError("Write back is not permitted on a read-only cube.")
        dest_slice:Cell = Cell(cube=self, adress=address)
        dest_slice.value = value

    def __delitem__(self, address):
        """
        Deletes the records represented by the given address from the underlying
        dataframe of the cube.
        Args:
            address:
                A valid cube address.
                Please refer the documentation for further details.
        Raises:
            PermissionError:
                If write back is attempted on a read-only Cube.
        """
        if self._read_only:
            raise PermissionError("Write back is not permitted on a read-only cube.")
        dest_slice: Cell = Cell(self, address=address)
        self._delete(dest_slice._row_mask)

    def cell(self, address) -> Cell:
        """
        Returns a cell of the cube for a given address.
        Tip: Use indexed access `cell[ ... ]` for better readability.
        Args:
            address:
                A valid cube address.
                Please refer the documentation for further details.

        Returns:
            A Cell object that represents the cube data related to the address.

        Raises:
            ValueError:
                If the address is not valid or can not be resolved.
        """
        return Cell(self, address=address)

    def slice(self, rows=None, columns=None, filters=None) -> Slice:
        """
        Returns a new slice for the cube. A slice represents a table-alike view to data in the cube.
        Typically, a slice has rows, columns and filters, comparable to an Excel PivotTable.
        Useful for printing in Jupyter, visual data analysis and reporting purposes.
        Slices can be easily 'navigated' by setting and changing rows, columns and filters.

        Please refer to the documentation of the Slice class for further details.

        Samples:
            >>> cdf = cubed(df)
            >>> cdf.slice(rows="product", columns="region", filters={"year": 2020})
            ------------------------------------
            year: 2000
            ------------------------------------
            |         | (all) | North | South |
            ------------------------------------
            | (all)   |   550 |   300 |   250 |
            | Apple   |   200 |   100 |   100 |
            | Banana  |   350 |   200 |   150 |
        """
        raise NotImplementedError("Not implemented yet. Sorry...")

    @property
    def sum(self):
        """
        Returns:
            The sum of the values for a given address.
        """
        return self._sum_op

    @property
    def avg(self):
        """
        Returns:
            The average of the values for a given address.
        """
        return self._avg_op

    @property
    def median(self):
        """
        Returns:
            The median of the values for a given address.
        """
        return self._median_op

    @property
    def min(self):
        """
        Returns:
            The minimum of the values for a given address.
        """
        return self._min_op

    @property
    def max(self):
        """
        Returns:
            The maximum of the values for a given address.
        """
        return self._max_op

    @property
    def count(self):
        """
        Returns:
            The number of records matching the given address.
        """
        return self._count_op

    @property
    def stddev(self):
        """
        Returns:
            The standard deviation of the values for a given address.
        """
        return self._stddev_op

    @property
    def var(self):
        """
        Returns:
            The variance of the values for a given address.
        """
        return self._var_op

    @property
    def pof(self):
        """
        Returns:
            The percentage of the sum of values for a given address related to all values in the data frame.
        """
        return self._pof_op

    @property
    def nan(self):
        """
        Returns:
            The number of non-numeric values for a given address. 'nan' stands for 'not a number'.
        """
        return self._nan_op

    @property
    def an(self):
        """Returns:
            The number of numeric values for a given address. 'an' stands for 'a number'.
        """
        return self._an_op

    @property
    def zero(self):
        """
        Returns:
            The number of zero values for a given address.
         """
        return self._zero_op

    @property
    def nzero(self):
        """
        Returns:
            The number of non-zero values for a given address.
        """
        return self._nzero_op
    # endregion

    # region Internal methods for data preparation and querying
    def _prepare(self):
        # if self.schema
        raise NotImplementedError("Not implemented yet")

    @staticmethod
    def _islist(item):
        return isinstance(item, List) or isinstance(item, Tuple)

    def _write_back(self, row_mask: np.ndarray | None = None, measure: Any = None, value: Any = None):
        """Writes back a value for a given address in the cube."""
        raise NotImplementedError("Not implemented yet")

    def _evaluate(self, row_mask, measure, operation: CubeAggregationFunctionType = CubeAggregationFunctionType.SUM):
        # Get values to aggregate using Numpy (slightly faster than using Pandas)
        # Note: The next statement does not generate some copy of the data, but returns a reference
        #       to internal Numpy ndarray of the Pandas dataframe. So, its memory efficient and fast.

        if measure is None :
            # special cases: if no measure is defined, always return the number of records.
            return len(row_mask)
        elif row_mask is None:
            # special cases: if no row_mask is defined, then process all records.
            values = self._df[measure.column].to_numpy()
        else:
            values = self._df[measure.column].to_numpy()
            if len(row_mask) == 0:
                return 0
        values: np.ndarray = values[row_mask]

        match operation:
            case CubeAggregationFunctionType.SUM:
                value = np.nansum(values)
            case CubeAggregationFunctionType.AVG:
                value = np.nanmean(values)
            case CubeAggregationFunctionType.MEDIAN:
                value = np.nanmedian(values)
            case CubeAggregationFunctionType.MIN:
                value = np.nanmin(values)
            case CubeAggregationFunctionType.MAX:
                value = np.nanmax(values)
            case CubeAggregationFunctionType.COUNT:
                value = len(values)
            case CubeAggregationFunctionType.STD:
                value = np.nanstd(values)
            case CubeAggregationFunctionType.VAR:
                value = np.nanvar(values)
            case CubeAggregationFunctionType.POF:
                value = np.nansum(values) / self.df[str(measure)].sum()
            case CubeAggregationFunctionType.NAN:
                value = np.count_nonzero(np.isnan(values))
            case CubeAggregationFunctionType.AN:
                value = np.count_nonzero(~np.isnan(values))
            case CubeAggregationFunctionType.ZERO:
                value = np.count_nonzero(values == 0)
            case CubeAggregationFunctionType.NZERO:
                value = np.count_nonzero(values)
            case _:
                value = np.nansum(values) # default operation is SUM

        if self._convert_values_to_python_data_types:
            value = self._convert_to_python_type(value)
        return value

    def _allocate(self, row_mask: np.ndarray | None = None, measure: Any = None, value: Any = None,
                    operation: CubeAllocationFunctionType = CubeAllocationFunctionType.DISTRIBUTE):
        """Allocates a value for a given address in the cube."""

        # Get values to updates or delete
        value_series = self._df[measure.column].to_numpy()
        values: np.ndarray = value_series[row_mask]

        # update values based on the requested operation
        match operation:
            case CubeAllocationFunctionType.DISTRIBUTE:
                current = sum(values)
                if current != 0:
                    values = values / current * value
            case CubeAllocationFunctionType.SET:
                values = np.full_like(values, value)
            case CubeAllocationFunctionType.DELTA:
                values = values + value
            case CubeAllocationFunctionType.MULTIPLY:
                values = values * value
            case CubeAllocationFunctionType.ZERO:
                values = np.zeros_like(values)
            case CubeAllocationFunctionType.NAN:
                values = np.full_like(values, np.nan)
            case CubeAllocationFunctionType.DEL:
                raise NotImplementedError("Not implemented yet")
            case _:
                raise ValueError(f"Allocation operation {operation} not supported.")

        # update the values in the dataframe
        updated_values = pd.DataFrame({measure.column: values}, index=row_mask)
        self._df.update(updated_values)

    def _delete(self, row_mask: np.ndarray | None = None, measure: Any = None):
        """Deletes all rows for a given address."""
        self._df.drop(index=row_mask, inplace=True, errors="ignore")
        # not yet required:  self._df.reset_index(drop=True, inplace=True)
        pass


    def _address_to_args(self, address) -> list:
        """Converts an address into a list of dicts of typed arguments."""
        args = []
        if not self._islist(address):
            address = [address,]
        for index, argument in enumerate(address):
            if isinstance(argument, dict):
                for key, value in argument.items():
                    args.append({"column": key, "arg": value})

            elif isinstance(argument, str):
                    parts = argument.split(":")
                    if len(parts) == 2:
                        args.append({"column": parts[0].strip(), "arg":  parts[1]})
                    else:
                        args.append({"column": "?", "arg":  argument})

            elif isinstance(argument, Filter):
                args.append({"column":argument.column, "arg":  argument})

            else:
                args.append({"column":"?", "arg":  argument})
        return args

    def _resolve_address_new(self, address, row_mask: np.ndarray | None = None,
                         measure: Measure | str |None = None, dynamic_access:bool = False) -> (np.ndarray, Any):
        """
        Resolves an address to a row mask and a measure.
        Likely, the most important method of the Cube class.

        :param address: The address to be resolved.
        :param measure: The measure to be used for the aggregation.
        :param row_mask: A row mask to be used for subsequent address resolution.
        :param dynamic_access: If True, the address is resolved for a dynamic call, e.g. cube.Online.Apple.cost
        :return: The row mask and the measure to be used for the aggregation.
        """
        # special case: "*" as address, return all values of the cube or current context
        if address == "*":
            if measure is None:  # Use the first measure as default if no measure is specified.
                if len(self._measures) > 0:
                    measure = self._measures[0]
            if row_mask is None:
                row_mask = self._df.index.to_numpy()
            return row_mask, measure

        unresolved_arguments: list[dict] = []   # arguments of the address that could not be resolved in the first run
        resolved_dims: set[Dimension] = set()   # dimensions that have been resolved
        measure = None

        # 1. run: resolve all arguments that can be resolved directly
        arguments = self._address_to_args(address)
        for argument in arguments:
            column = argument["column"]
            arg = argument["arg"]

            # 1.1 evaluate Filter arguments
            if isinstance(arg, Filter):
                if row_mask is None:
                    row_mask = arg.mask
                else:
                    row_mask =  np.intersect1d(arg.mask, row_mask)
                resolved_dims.update(arg.dimensions)

            # 1.2 evaluate string arguments
            elif isinstance(arg, str):
                # 1.2.1 Check for measure names first, they have the highest priority for address resolution
                if arg in self._measures:
                    if measure and ( not dynamic_access):
                        raise ValueError(f"Too many measures in address. "
                                         f"At least 2 measures found in address ({measure}, {arg}), "
                                         f"but just 1 measure is allowed in an address.")
                    measure = self._measures[arg]
                    continue

                # 1.2.2 Try to process an unspecific address without a dimension, e.g. "A" or "42"
                if column == "?":
                    # dimension not specified, try to resolve the member in all dimensions
                    resolved = False
                    for dimension in (self._dimensions.to_set - resolved_dims):
                        resolved = dimension.contains(arg)
                        if resolved:
                            row_mask = dimension._resolve(arg, row_mask)
                            resolved_dims.add(dimension)
                            break

                    if resolved:
                        continue
                    else:
                        unresolved_arguments.append(argument)

                # 1.2.3 Try to process a specific address with a dimension, e.g. "product:A"
                else:
                    # dimension specified, try to resolve the dimension and the member
                    if not column in self._dimensions:
                        raise ValueError(f"Failed to resolve address '{address}'. "
                                         f"A dimension named '{column}' as defined in argument '{column}:{arg}' "
                                         f"is not contained in the cube schema.")

                    dimension = self._dimensions[column]
                    resolved = dimension.contains(arg)
                    if resolved:
                        row_mask = dimension._resolve(arg, row_mask)
                        resolved_dims.add(dimension)
                        continue

                    # check for wildcard members
                    if "*" in arg or "?" in arg:
                        members = dimension._resolve_wildcard_members(arg)
                        if len(members) > 0:
                            row_mask = dimension._resolve(members, row_mask)
                        resolved_dims.add(dimension)
                    else:
                        unresolved_arguments.append(argument)

            # 1.3 evaluate date arguments
            elif isinstance(arg, (datetime, np.datetime64)):
                if column == "?":
                    resolved = False
                    for dimension in (self._dimensions.to_set - resolved_dims):
                        if is_datetime(dimension.dtype):
                            row_mask = dimension._resolve(arg, row_mask)
                            resolved_dims.add(dimension)
                            resolved = True
                            continue
                    if not resolved:
                        raise ValueError(f"Failed to resolve address '{address}'. "
                                         f"Datetime member '{arg}' does not seem to match any dimension.")

                else:
                    if not column in self._dimensions:
                        raise ValueError(f"Failed to resolve address '{address}'. "
                                         f"A dimension named '{column}' as defined in argument '{column}:{arg}' "
                                         f"is not contained in the cube schema.")
                    dimension = self._dimensions[column]
                    if is_datetime(dimension.dtype):
                        row_mask = dimension._resolve(arg, row_mask)
                        resolved_dims.add(dimension)
                        continue
                    else:
                        raise ValueError(f"Failed to resolve address '{address}'. "
                                         f"Dimension '{column}' is of type 'datetime', "
                                         f"but argument '{column}:{arg}' is of type '{type(arg).__name__}'.")

            else:
                # All other data types are considered as members of dimensions!
                # ...first with check common Python datatypes (int, bool, float) against
                #    dimensions with same/corresponding dtype.
                if column == "?":
                    for dimension in (self._dimensions.to_set - resolved_dims):
                        # ensure to check dimensions with a suitable data type
                        if ((isinstance(arg, int) and is_integer_dtype(dimension.dtype)) or
                                (isinstance(arg, bool) and is_bool_dtype(dimension.dtype)) or
                                (isinstance(arg, float) and is_float_dtype(dimension.dtype))):
                            row_mask = dimension._resolve(arg, row_mask)
                            # Note: if the member could be found in multiple dimensions, the first one is used.
                            #       this may lead to unexpected results, and can only be resolved by
                            #       providing the dimension name in the address,
                            #       e.g. {"dim_name": 1"}, {"dim_name": True"} etc.
                            if len(row_mask) > 0:
                                resolved_dims.add(dimension)
                                continue

                    # ...second we just use the first dimension that responds to the member
                    for dimension in (self._dimensions.to_set - resolved_dims):
                        row_mask = dimension._resolve(arg, row_mask)
                        if len(row_mask) > 0:
                            resolved_dims.add(dimension)
                            continue
                else:
                    if not column in self._dimensions:
                        raise ValueError(f"Failed to resolve address '{address}'. "
                                         f"A dimension named '{column}' as defined in argument '{column}:{arg}' "
                                         f"is not contained in the cube schema.")

                    dimension = self._dimensions[column]
                    if ((isinstance(arg, int) and is_integer_dtype(dimension.dtype)) or
                            (isinstance(arg, bool) and is_bool_dtype(dimension.dtype)) or
                            (isinstance(arg, float) and is_float_dtype(dimension.dtype))):
                        row_mask = dimension._resolve(arg, row_mask)
                        # Note: if the member could be found in multiple dimensions, the first one is used.
                        #       this may lead to unexpected results, and can only be resolved by
                        #       providing the dimension name in the address,
                        #       e.g. {"dim_name": 1"}, {"dim_name": True"} etc.
                        if len(row_mask) > 0:
                            resolved_dims.add(dimension)
                            continue

                    # ...second we just use the first dimension that responds to the member
                    row_mask = dimension._resolve(arg, row_mask)
                    if len(row_mask) > 0:
                        resolved = True
                        continue

                # we failed to resolve the member in any dimension
                unresolved_arguments.append(arg)

        # 2. run: resolve all arguments that could not be resolved in the first run
        if len(unresolved_arguments) > 0:
            if len(self._dimensions) == 0:
                # special case: No dimensions defined in the cube schema
                raise ValueError(f"Failed to resolve address '{address}'. "
                                 f"No dimensions are available in the cube or schema.")
            else:
                raise ValueError(f"Failed to resolve address '{address}'. {len(unresolved_arguments)}x unresolved "
                                 f"member{'s' if len(unresolved_arguments) > 1 else ''}: {unresolved_arguments}. "
                                 f"No dimension contains this member{'s' if len(unresolved_arguments) > 1 else ''}.")

        if measure is None:  # Use the first measure as default if no measure is specified.
            if len(self._measures) > 0:
                measure = self._measures[0]

        return row_mask, measure


    def _resolve_address(self, address, row_mask: np.ndarray | None = None,
                         measure: Measure | str | None = None, dynamic_access: bool = False) -> (np.ndarray, Any):

        # **** Old implementation of address resolution ****
        resolved_dims: set[Dimension] = set()   # dimensions that have been resolved
        measure = None
        unresolved_parts = []   # parts of the address that could not be resolved from dimensions or measures

        # 0. process special cases first
        # **********************************************************************
        # 0.1 special case "*": return all values of the cube or current context
        if address == "*":
            if measure is None:  # Use the first measure as default if no measure is specified.
                if len(self._measures) > 0:
                    measure = self._measures[0]
            if row_mask is None:
                row_mask = self._df.index.to_numpy()
            return row_mask, measure


        # 1. Process all available arguments of the address
        # *************************************************
        if not self._islist(address):
            address = [address,]
        for index, arg in enumerate(address):

            # 1.1 Filter object: we can evaluate it and instantly return the row mask
            if isinstance(arg, Filter):
                # Evaluate the filter and return the row mask
                if row_mask is None:
                    row_mask = arg.mask
                else:
                    row_mask =  np.intersect1d(arg.mask, row_mask)

            # 1.2 Dict: we can resolve the members of the dimensions
            #     e.g.: {"product": "A"} or {"product": ["A", "B", "C"]} is expected...
            elif isinstance(arg, dict):
                # todo: requires rework
                for dimension, member in arg.items():
                    # process only those dimensions that have not been resolved yet (to avoid conflicts)
                    if dimension in self._dimensions:
                        dim = self._dimensions[dimension]
                        row_mask = dim._resolve(member, row_mask)
                        resolved_dims.add(dim)
                    else:
                        raise ValueError(f"Failed to resolve address '{address}'. "
                                         f"A dimension named '{dimension}' as defined in argument '{arg}'"
                                         f" is not defined in cube schema.")


            # 1.3 A list of members from a single dimension is expected,
            #     e.g. ("A", "B", "C") from dimension xyz
            elif self._islist(arg):
                # todo: requires rework

                # Note: an empty tuple is allowed and means all members of whatever measure,
                # e.g. cube[()] returns the sum of all values in the cube. As this operation has no
                # effect on the row_mask, it is not necessary to process it.
                if len(arg) > 0:
                    dimension = None
                    resolved = False
                    for dimension in (self._dimensions.to_set - resolved_dims):
                        resolved = dimension.contains(arg)
                        if resolved:
                            resolved_dims.add(dimension)
                            dimension = dimension
                            break
                    if not resolved:
                        raise ValueError(f"Failed to resolve address '{address}'. The members "
                                         f"defined in argument '{arg}' are not from the same dimension "
                                         f"or can not be found in any dimension.")
                    row_mask = dimension._resolve(arg, row_mask)

            # 1.4 Anything else, likely a single value from a single measure,
            #     e.g. "A" or 42 or a measure name
            else:
                resolved = False
                if isinstance(arg, str):
                    # Check for measure names first
                    if arg in self._measures:
                        if measure and ( not dynamic_access):
                            raise ValueError(f"Too many measures. "
                                             f"At least 2 measures found in address ({measure}, {arg}), "
                                             f"but just 1 measure is allowed in an address.")
                        measure = self._measures[arg]
                        resolved = True
                    else:
                        # Check if the part contains a measure and a member, e.g. "product:A".
                        if ":" in arg:
                            parts = arg.split(":")
                            dimension = parts[0].strip()
                            member = parts[1].strip()
                            if dimension in self._dimensions:
                                if "*" in member or "?" in member:
                                    members = self._dimensions[dimension]._resolve_wildcard_members(member)
                                    if len(members) > 0:
                                        row_mask = self._dimensions[dimension]._resolve(members, row_mask)
                                        resolved = True
                                else:
                                    row_mask = self._dimensions[dimension]._resolve(member, row_mask)
                                    resolved = True

                        if not resolved:
                            # No measure specified, try to resolve the member in all dimensions.
                            # This can be a very exhaustive operation, but it is necessary to support
                            # addresses like ("A", "B", "C") where the members are from different dimensions
                            for dimension in (self._dimensions.to_set - resolved_dims):
                                resolved = dimension.contains(arg)
                                if resolved:
                                    row_mask = self._dimensions[dimension]._resolve(arg, row_mask)
                                    resolved_dims.add(dimension)
                                    break
                    if not resolved:
                        unresolved_parts.append(arg)

                elif isinstance(arg, (datetime, np.datetime64)):
                    for dimension in (self._dimensions.to_set - resolved_dims):
                        if is_datetime(dimension.dtype):
                            row_mask = dimension._resolve(arg, row_mask)
                            resolved_dims.add(dimension)
                            resolved = True
                            break
                    if not resolved:
                        unresolved_parts.append(arg)
                else:
                    # All other data types are considered as members of dimensions!
                    # ...first with check common Python datatypes (int, bool, float) against
                    #    dimensions with same/corresponding dtype.
                    for dimension in (self._dimensions.to_set - resolved_dims):
                        # ensure to check dimensions with a suitable data type
                        if ((isinstance(arg, int) and is_integer_dtype(dimension.dtype)) or
                                (isinstance(arg, bool) and is_bool_dtype(dimension.dtype)) or
                                (isinstance(arg, float) and is_float_dtype(dimension.dtype))):
                            row_mask = dimension._resolve(arg, row_mask)
                            # Note: if the member could be found in multiple dimensions, the first one is used.
                            #       this may lead to unexpected results, and can only be resolved by
                            #       providing the dimension name in the address,
                            #       e.g. {"dim_name": 1"}, {"dim_name": True"} etc.
                            if len(row_mask) > 0:
                                resolved_dims.add(dimension)
                                resolved = True
                                break
                    if not resolved:
                        # ...second we just use the first dimension that responds to the member
                        for dimension in (self._dimensions.to_set - resolved_dims):
                            row_mask = dimension._resolve(arg, row_mask)
                            if len(row_mask) > 0:
                                resolved = True
                                break

                if not resolved:
                    unresolved_parts.append(arg)


        if len(unresolved_parts) > 0:
            if len(self._dimensions) == 0:
                # special case: No dimensions defined in the cube schema
                raise ValueError(f"Failed to resolve address '{address}'. "
                                 f"No dimensions are available in the cube or schema.")
            else:
                raise ValueError(f"Failed to resolve address '{address}'. {len(unresolved_parts)}x unresolved "
                                 f"member{'s' if len(unresolved_parts) > 1 else ''}: {unresolved_parts}. "
                                 f"No dimension contains this member{'s' if len(unresolved_parts) > 1 else ''}.")

        if measure is None:  # Use the first measure as default if no measure is specified.
            if len(self._measures) > 0:
                measure = self._measures[0]

        return row_mask, measure

    def _resolve_address_modifier(self, address, row_mask: np.ndarray | None = None,
                                  measure: Measure | str |None = None, dynamic_access:bool = False):
        """Modifies an address for a given operation."""
        row_mask, measure = self._resolve_address(address, row_mask, measure, dynamic_access)
        return row_mask, measure


    @staticmethod
    def _convert_to_python_type(value):
        if isinstance(value, (np.integer, int)):
            return int(value)
        elif isinstance(value, (np.floating, float)):
            return float(value)
        elif isinstance(value, (np.datetime64, pd.Timestamp)):
            return pd.Timestamp(value).to_pydatetime()
        elif isinstance(value, (np.bool_, bool)):
            return bool(value)
        elif isinstance(value, (np.ndarray, pd.Series, list, tuple)):
            if isinstance(value, np.ndarray):
                value = value.tolist()
            return [Cube._convert_to_python_type(v) for v in value]
        else:
            return value

    # endregion



