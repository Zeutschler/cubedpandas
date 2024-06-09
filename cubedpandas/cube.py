from types import ModuleType, FunctionType
from gc import get_referents
from typing import Any, List, Tuple, TYPE_CHECKING
import sys
import numpy as np
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype as is_datetime
from datetime import datetime


#if TYPE_CHECKING:
from cube_aggregation import CubeAggregationFunctionType
from cube_aggregation import CubeAggregationFunction

from schema import Schema
from measure_collection import MeasureCollection
from measure import Measure
from dimension_collection import DimensionCollection
from caching_strategy import CachingStrategy, EAGER_CACHING_THRESHOLD
from slice import Slice


class Cube:
    """Wraps a Pandas dataframe with a multi-dimensional data cube for simple and fast cell based data access
    to numerical values from the underlying dataframe. The multi-dimensional cube schema, containing the dimensions and
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
    def __getitem__(self, address):
        return Slice(self, address)
        return self._get(CubeAggregationFunctionType.SUM, address)

    def __setitem__(self, address, value):
        raise NotImplementedError("Not implemented yet")

    def slice(self, address) -> Slice:
        """
        Returns a slice of the cube for a given address.

        A slice represents a multi-dimensional data cell or data area in a cube. Slice objects can
        be used to navigate through and interact with the data space of a cube and the underlying dataframe.
        Slices behave like float values and can be directly used in mathematical calculations that read from
        or write to a cube.

        Sample usage:

        .. code:: python
            import cubedpandas as cpd

            df = get_your_dataframe()
            cube = cpd.Cube(df)

            # get a value from the cube and add 19% VAT
            net_value = cube.slice("2024", "Aug", "Germany", "NetSales")
            gross_sales_usa = net_value * 1.19

            # create new data or overwrite data for 2025 by copying all 2024 prices and adding 5% inflation
            cube.slice("2025", "Price") = cube.slice("2024", "Price") * 1.05
        """
        #return Slice.create(self, address)
        return Slice(self, address)

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
    # endregion

    # region Internal methods for data preparation and querying
    def _prepare(self):
        # if self.schema
        raise NotImplementedError("Not implemented yet")

    @staticmethod
    def _islist(item):
        return isinstance(item, List) or isinstance(item, Tuple)

    def _get(self, operation: 'CubeAggregationFunctionType', address, row_mask: np.ndarray | None = None):
        """Evaluates an aggregation operation for a given address in the cube."""
        # Resolve address and get the row mask for the address
        row_mask, measure = self._resolve_address(address, row_mask)

        # Execute aggregation function on matching data
        return self._evaluate(row_mask, measure, operation)

    def _delete(self, row_mask: np.ndarray | None = None, measure: Any = None):
        """Deletes all values for a given address in the cube."""
        raise NotImplementedError("Not implemented yet")

    def _write_back(self, row_mask: np.ndarray | None = None, measure: Any = None, value: Any = None):
        """Writes back a value for a given address in the cube."""
        raise NotImplementedError("Not implemented yet")

    def _evaluate(self, row_mask, measure, operation: CubeAggregationFunctionType = CubeAggregationFunctionType.SUM):
        # Get values to aggregate using Numpy (slightly faster than using Pandas)
        # Note: The next statement does not generate some copy of the data, but returns a reference
        #       to internal Numpy ndarray of the Pandas dataframe. So, its memory efficient and fast.
        value_series = self._df[measure.column].to_numpy()
        records: np.ndarray = value_series[row_mask]

        match operation:
            case CubeAggregationFunctionType.SUM:
                value = np.nansum(records)
            case CubeAggregationFunctionType.AVG:
                value = np.nanmean(records)
            case CubeAggregationFunctionType.MEDIAN:
                value = np.nanmedian(records)
            case CubeAggregationFunctionType.MIN:
                value = np.nanmin(records)
            case CubeAggregationFunctionType.MAX:
                value = np.nanmax(records)
            case CubeAggregationFunctionType.COUNT:
                value = len(records)
            case CubeAggregationFunctionType.STD:
                value = np.nanstd(records)
            case CubeAggregationFunctionType.VAR:
                value = np.nanvar(records)
            case CubeAggregationFunctionType.POF:
                value = np.nansum(records) / self.df[measure].sum()
            case CubeAggregationFunctionType.NAN:
                value = np.count_nonzero(np.isnan(records))
            case CubeAggregationFunctionType.AN:
                value = np.count_nonzero(~np.isnan(records))
            case CubeAggregationFunctionType.ZERO:
                value = np.count_nonzero(records == 0)
            case CubeAggregationFunctionType.NZERO:
                value = np.count_nonzero(records)
            case _:
                value = np.nansum(records) # default operation is SUM

        if self._convert_values_to_python_data_types:
            value = self._convert_to_python_type(value)
        return value

    def _set(self, address, value):
        """Sets a value for a given address in the cube."""
        raise NotImplementedError("Not implemented yet")

    def _resolve_address(self, address, row_mask: np.ndarray | None = None, measure: Measure | str |None = None) -> (np.ndarray, Any):
        """Resolves an address to a row mask and a measure.
        :param address: The address to be resolved.
        :param row_mask: A row mask to be used for subsequent address resolution.
        :return: The row mask and the measure to be used for the aggregation.
        """
        # 1. Process all arguments of the address
        unresolved_parts = []   # parts of the address that could not be resolved from dimensions or measures
        if not self._islist(address):
            address = [address,]
        for index, part in enumerate(address):

            # Parse and evaluate the argument
            if isinstance(part, dict):
                # Something like {"product": "A"} or {"product": ["A", "B", "C"]} is expected...
                if len(part) != 1:
                    raise ValueError(f"Error in address argument {index}. Only 1 dimension is allowed in a dictionary "
                                     f"address argument, but {len(part)} where found. "
                                     f"Valid sample: {{'product': ['A', 'B', 'C']}}")
                dimension = list(part.keys())[0]
                members = part[dimension]
                if dimension in self._dimensions:
                    row_mask = self._dimensions[dimension]._resolve(members, row_mask)
                else:
                    raise ValueError(f"Error in address argument {index}. "
                                     f"Dimension '{dimension}' not found in cube schema.")


            elif self._islist(part): # a tuple of members from 1 measure ("A", "B", "C")
                # A list of members from a single measure is expected, e.g. ("A", "B", "C")

                # Note: an empty tuple is allowed and means all members of whatever measure,
                # e.g. cube[()] returns the sum of all values in the cube. As this operation has no
                # effect on the row_mask, it is not necessary to process it.
                if len(part) > 0:
                    dimension = None
                    resolved = False
                    for dimension in self._dimensions:
                        resolved = dimension.contains(part)
                        if resolved:
                            dimension = dimension
                            break
                    if not resolved:
                        raise ValueError(f"Error in address argument {index}. "
                                         f"Members '{part}' are not from the same dimension "
                                         f"or not found in any dimension.")
                    row_mask = dimension._resolve(part, row_mask)

            else: # a single value from a single measure, e.g. "A" or 42 or a measure name
                resolved = False

                if isinstance(part, str):
                    # Check for measure names first
                    if part in self._measures:
                        if measure:
                            raise ValueError("Multiple measures found in address, but only one measure is allowed.")
                        measure = self._measures[part]
                        resolved = True
                    else:
                        # Check if the part contains a measure and a member, e.g. "product:A".
                        if ":" in part:
                            parts = part.split(":")
                            dimension = parts[0].strip()
                            member = parts[1].strip()
                            if dimension in self._dimensions:
                                row_mask = self._dimensions[dimension]._resolve(member, row_mask)
                                resolved = True

                        if not resolved:
                            # No measure specified, try to resolve the member in all dimensions.
                            # This can be a very exhaustive operation, but it is necessary to support
                            # addresses like ("A", "B", "C") where the members are from different dimensions
                            for dimension in self._dimensions:
                                resolved = dimension.contains(part)
                                if resolved:
                                    row_mask = self._dimensions[dimension]._resolve(part, row_mask)
                                    break
                    if not resolved:
                        unresolved_parts.append(part)

                elif isinstance(part, (datetime, np.datetime64)):
                    for dimension in self._dimensions:
                        if is_datetime(dimension.dtype):
                            row_mask = self._dimensions[dimension]._resolve(part, row_mask)
                            resolved = True
                    if not resolved:
                        unresolved_parts.append(part)

        if len(unresolved_parts) > 1:
            raise ValueError(f"Multiple unresolved member arguments found in address: {unresolved_parts}")

        if measure is None:  # Use the first measure as default if no measure is specified.
            measure = self._measures[0]

        return row_mask, measure

    def _resolve_address_modifier(self, address, row_mask: np.ndarray | None = None, measure: Measure | str |None = None):
        """Modifies an address for a given operation."""
        row_mask, measure = self._resolve_address(address, row_mask)
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



