# cube.py
# CubedPandas - Multi-dimensional data analysis for Pandas dataframes.
# ©2024 by Thomas Zeutschler. All rights reserved.
# MIT License - please see the LICENSE file that should have been included in this package.

import sys
from types import ModuleType, FunctionType
from gc import get_referents
from typing import Any, List, Tuple
from datetime import datetime
import numpy as np
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype as is_datetime

from cubedpandas.cube_aggregation import CubeAggregationFunctionType, CubeAggregationFunction, CubeAllocationFunctionType
from cubedpandas.schema import Schema
from cubedpandas.measure_collection import MeasureCollection
from cubedpandas.measure import Measure
from cubedpandas.dimension_collection import DimensionCollection
from cubedpandas.caching_strategy import CachingStrategy, EAGER_CACHING_THRESHOLD
from cubedpandas.cell import Cell
from cubedpandas.slice import Slice


class Cube:
    """Wrapper for Pandas dataframes to provide multi-dimensional access to mainly numerical values from
    the underlying dataframe. The multi-dimensional cube schema, containing the dimensions and
    measures of a cube, can be either inferred automatically from the underlying dataframe (default)
    or defined explicitly.

    In addition, easy to use methods to filter, slice, access and manipulate the underlying dataframe are provided.
    """

    def __init__(self, df: pd.DataFrame, schema=None,
                 infer_schema_if_not_provided: bool = True,
                 caching: CachingStrategy = CachingStrategy.LAZY,
                 caching_threshold: int = EAGER_CACHING_THRESHOLD,
                 enable_write_back: bool = False):
        """
        Initializes a new Cube wrapping and providing a Pandas dataframe as a multi-dimensional data cube.
        The schema of the Cube can be either inferred automatically from the dataframe  (default) or defined explicitly.

        :param df: The Pandas dataframe to wrap into a Cube.
        :param schema: The schema of the Cube. If not provided, the schema will be inferred from the dataframe if
                parameter `infer_schema_if_not_provided` is set to `True`.
        :param infer_schema_if_not_provided:  If True, the schema will be inferred from the dataframe if not provided.
        :param caching: The caching strategy to be used for the Cube. Default and recommended value for almost all use
                cases is `CachingStrategy.LAZY`, which caches dimension members on first access.
                Please refer to the documentation of 'CachingStrategy' for more information.
        :param caching_threshold: The threshold for EAGER caching. If the number of members in a dimension
                is below this threshold, the dimension will be cached eagerly.
                Default value is `EAGER_CACHING_THRESHOLD` := 256 members.
        :param enable_write_back: If True, the Cube will become write-back enable and changes to the data
                will be written to the underlying dataframe.
        """
        self._df: pd.DataFrame = df
        self._infer_schema: bool = infer_schema_if_not_provided
        self._enable_write_back: bool = enable_write_back
        self._caching: CachingStrategy = caching
        self._caching_threshold: int = caching_threshold

        # get and prepare the cube schema
        if (schema is None) and infer_schema_if_not_provided:
            schema = Schema(df).infer_schema()
        else:
            schema = Schema(df, schema, caching=caching)
        self._schema: Schema = schema
        self._dimensions: DimensionCollection = schema.dimensions
        self._measures: MeasureCollection = schema.measures

        # warm up cache, if required
        if caching >= CachingStrategy.EAGER:
            self._warm_up_cache()

        # data type conversion
        self._convert_values_to_python_data_types: bool = True

        # setup operations
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
    def schema(self) -> Schema:
        """Returns the schema of the Cube."""
        return self._schema

    @property
    def df(self) -> pd.DataFrame:
        """Returns the underlying Pandas dataframe of the Cube."""
        return self._df

    @property
    def dimensions(self) -> DimensionCollection:
        """Returns the dimensions of the Cube."""
        return self._schema.dimensions

    def __len__(self):
        return len(self._df)

    @property
    def memory_usage(self) -> int:
        """
        Returns the memory usage of the Cube object instance in bytes,
        memory for the underlying dataframe in not included."""
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
        """Clears the cache for all dimensions of the Cube."""
        for dimension in self._dimensions:
            dimension.clear_cache()
    # endregion

    # region Data Access Methods
    def __getattr__(self, name) -> Cell:
        # dynamic member or measure access
        # print(f"cube.__getattr__({name})")
        #if name in self._measures: # resolve measure first
        #    return Cell(self, address="*", measure=name, dynamic_access=True)
        return Cell(self, address=name, dynamic_access=True)

    def __getitem__(self, address) -> Cell:
        return Cell(self, address)

    def __setitem__(self, address, value):
        dest_slice:Cell = Cell(self, address)
        dest_slice.value = value
        # raise NotImplementedError("Not implemented yet")

    def __delitem__(self, address):
        dest_slice: Cell = Cell(self, address)
        self._delete(dest_slice._row_mask)

    def cell(self, address) -> Cell:
        """
        Returns a cell of the cube for a given address.

        A cell represents a multi-dimensional data cell or data area in a cube. Cell objects can
        be used to navigate through and interact with the data space of a cube and the underlying dataframe.
        Slices behave like float values and can be directly used in mathematical calculations that read from
        or write to a cube.

        Sample usage:

        .. code:: python
            import cubedpandas as cpd

            df = get_your_dataframe()
            cube = cpd.Cube(df)

            # get a value from the cube and add 19% VAT
            net_value = cube.cell("2024", "Aug", "Germany", "NetSales")
            gross_sales_usa = net_value * 1.19

            # create new data or overwrite data for 2025 by copying all 2024 prices and adding 5% inflation
            cube.cell("2025", "Price") = cube.cell("2024", "Price") * 1.05
        """
        return Cell(self, address)

    def slice(self, rows=None, columns=None, filters=None) -> Slice:
        """
        Returns a slice of the cube. A slice represents a view on a cube, and allows for easy
        access to the underlying Pandas dataframe. Typically, a slice has rows, columns and filter,
        just like in an Excel PivotTable. Slices are easy to define and use for convenient data analysis.

        Sample usage:

        .. code:: python
            pass
        """
        raise NotImplementedError("Not implemented yet. Sorry...")

    @property
    def sum(self):
        """Returns the sum of the values for a given address."""
        return self._sum_op

    @property
    def avg(self):
        """Returns the average of the values for a given address."""
        return self._avg_op

    @property
    def median(self):
        """Returns the median of the values for a given address."""
        return self._median_op

    @property
    def min(self):
        """Returns the minimum value for a given address."""
        return self._min_op

    @property
    def max(self):
        """Returns the maximum value for a given address."""
        return self._max_op

    @property
    def count(self):
        """Returns the number of the records matching a given address."""
        return self._count_op

    @property
    def stddev(self):
        """Returns the standard deviation of the values for a given address."""
        return self._stddev_op

    @property
    def var(self):
        """Returns the variance of the values for a given address."""
        return self._var_op

    @property
    def pof(self):
        """Returns the percentage of the sum of values for a given address related to all values in the data frame."""
        return self._pof_op

    @property
    def nan(self):
        """Returns the number of non-numeric values for a given address. 'nan' stands for 'not a number'"""
        return self._nan_op

    @property
    def an(self):
        """Returns the number of numeric values for a given address. 'an' stands for 'a number'"""
        return self._an_op

    @property
    def zero(self):
        """Returns the number of zeros for a given address."""
        return self._zero_op

    @property
    def nzero(self):
        """Returns the number of non-zero values for a given address."""
        return self._nzero_op

    # endregion

    # region Internal methods for data preparation and querying
    def _prepare(self):
        # if self.schema
        raise NotImplementedError("Not implemented yet")

    @staticmethod
    def _islist(item):
        return isinstance(item, List) or isinstance(item, Tuple)

    # def _get(self, operation: 'CubeAggregationFunctionType', address, row_mask: np.ndarray | None = None):
    #     """Evaluates an aggregation operation for a given address in the cube."""
    #     # Resolve address and get the row mask for the address
    #     row_mask, measure = self._resolve_address(address, row_mask)
    #
    #     # Execute aggregation function on matching data
    #     return self._evaluate(row_mask, measure, operation)

    # def _set(self, address, value):
    #     """Sets a value for a given address in the cube."""
    #     raise NotImplementedError("Not implemented yet")


    def _write_back(self, row_mask: np.ndarray | None = None, measure: Any = None, value: Any = None):
        """Writes back a value for a given address in the cube."""
        raise NotImplementedError("Not implemented yet")

    def _evaluate(self, row_mask, measure, operation: CubeAggregationFunctionType = CubeAggregationFunctionType.SUM):
        # Get values to aggregate using Numpy (slightly faster than using Pandas)
        # Note: The next statement does not generate some copy of the data, but returns a reference
        #       to internal Numpy ndarray of the Pandas dataframe. So, its memory efficient and fast.
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
                value = np.nansum(values) / self.df[measure].sum()
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

    def _resolve_address(self, address, row_mask: np.ndarray | None = None,
                         measure: Measure | str |None = None, dynamic_access:bool = False) -> (np.ndarray, Any):
        """Resolves an address to a row mask and a measure.
        :param address: The address to be resolved.
        :param measure: The measure to be used for the aggregation.
        :param row_mask: A row mask to be used for subsequent address resolution.
        :param dynamic_access: If True, the address is resolved for a dynamic call, e.g. cube.Online.Apple.cost
        :return: The row mask and the measure to be used for the aggregation.
        """
        # 1. Process all arguments of the address
        unresolved_parts = []   # parts of the address that could not be resolved from dimensions or measures

        if address == "*":  # special case "*" return all values of the cube or current context
            if measure is None:  # Use the first measure as default if no measure is specified.
                measure = self._measures[0]
            if row_mask is None:
                row_mask = self._df.index.to_numpy()
            return row_mask, measure

        if not self._islist(address):
            address = [address,]
        for index, arg in enumerate(address):

            # Parse and evaluate the argument
            if isinstance(arg, dict):
                # Something like {"product": "A"} or {"product": ["A", "B", "C"]} is expected...
                for dimension, member in arg.items():
                    if dimension in self._dimensions:
                        row_mask = self._dimensions[dimension]._resolve(member, row_mask)
                    else:
                        raise ValueError(f"Error in address argument {arg}. "
                                         f"Dimension '{dimension}' is not defined in cube schema.")

            elif self._islist(arg):
                # A list of members from a single measure is expected, e.g. ("A", "B", "C")

                # Note: an empty tuple is allowed and means all members of whatever measure,
                # e.g. cube[()] returns the sum of all values in the cube. As this operation has no
                # effect on the row_mask, it is not necessary to process it.
                if len(arg) > 0:
                    dimension = None
                    resolved = False
                    for dimension in self._dimensions:
                        resolved = dimension.contains(arg)
                        if resolved:
                            dimension = dimension
                            break
                    if not resolved:
                        raise ValueError(f"Error in address argument {index}. "
                                         f"Members '{arg}' are not from the same dimension "
                                         f"or not found in any dimension.")
                    row_mask = dimension._resolve(arg, row_mask)

            else: # a single value from a single measure, e.g. "A" or 42 or a measure name
                resolved = False

                if isinstance(arg, str):
                    # Check for measure names first
                    if arg in self._measures:
                        if measure and ( not dynamic_access):
                            raise ValueError("Multiple measures found in address, but only one measure is allowed.")
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
                                        row_mask = self._dimensions[dimension]._resolve(member, row_mask)
                                        resolved = True
                                else:
                                    row_mask = self._dimensions[dimension]._resolve(member, row_mask)
                                    resolved = True

                        if not resolved:
                            # No measure specified, try to resolve the member in all dimensions.
                            # This can be a very exhaustive operation, but it is necessary to support
                            # addresses like ("A", "B", "C") where the members are from different dimensions
                            for dimension in self._dimensions._dims.values():
                                resolved = dimension.contains(arg)
                                if resolved:
                                    row_mask = self._dimensions[dimension]._resolve(arg, row_mask)
                                    break
                    if not resolved:
                        unresolved_parts.append(arg)

                elif isinstance(arg, (datetime, np.datetime64)):
                    for dimension in self._dimensions:
                        if is_datetime(dimension.dtype):
                            row_mask = self._dimensions[dimension]._resolve(arg, row_mask)
                            resolved = True
                    if not resolved:
                        unresolved_parts.append(arg)

        if len(unresolved_parts) > 1:
            raise ValueError(f"Multiple unresolved member arguments found in address: {unresolved_parts}")

        if measure is None:  # Use the first measure as default if no measure is specified.
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



