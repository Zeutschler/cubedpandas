import sys
from types import ModuleType, FunctionType
from gc import get_referents
from enum import IntEnum
import typing
import sys
import numpy as np
import pandas as pd
from datetime import datetime
from schema import Schema
from measure_collection import MeasureCollection
from dimension_collection import DimensionCollection
from caching_strategy import CachingStrategy
from dimension import Dimension

class CubeAggregationFunctionType(IntEnum):
    """Aggregation functions supported for the value in a cube.
    """
    SUM = 1
    AVG = 2
    MEDIAN = 3
    MIN = 4
    MAX = 5
    COUNT = 6
    STDDEV = 7
    VAR = 8
    POF = 9
    NAN = 10
    AN = 11

class Cube:
    """Wraps and provides a Pandas dataframe as a multi-dimensional data cube for simple and fast cell based data access
    to numerical values from the underlying dataframe. The multi-dimensional cube schema, aka as the dimensions and
    measures of a cube, can be either inferred automatically from the underlying dataframe (default) or defined explicitly.

    In addition, easy to use methods to filter, slice, access and manipulate the dataframe are provided.
    """

    def __init__(self, df: pd.DataFrame, schema=None,
                 infer_schema_if_not_provided: bool = True, enable_caching: bool = False,
                 enable_write_back: bool = False):
        """
        Initializes a new Cube wrapping and providing a Pandas dataframe as a multi-dimensional data cube.
        The schema of the Cube can be either inferred automatically from the dataframe  (default) or defined explicitly.

        :param df: The Pandas dataframe to wrap into a Cube.
        :param schema: The schema of the Cube. If not provided, the schema will be inferred from the dataframe if
                parameter 'infer_schema_if_not_provided' is set to True.
        :param infer_schema_if_not_provided:  If True, the schema will be inferred from the dataframe if not provided.
        :param enable_caching: If True, intermediate results are cached for faster data access.
        :param enable_write_back: If True, the Cube will be writeable and changes to the data will be written back to the
                underlying dataframe.
        """
        self._df: pd.DataFrame = df
        self._infer_schema: bool = infer_schema_if_not_provided
        self._enable_write_back: bool = enable_write_back
        self._enable_caching: bool = enable_caching

        if (schema is None) and infer_schema_if_not_provided:
            schema = Schema(df).infer_schema()
        else:
            schema = Schema(df, schema, enable_caching=enable_caching)
        self._schema: Schema = schema
        self._dimensions: DimensionCollection = schema.dimensions
        self._measures: MeasureCollection = schema.measures

        # setup operations
        self._sum_op = CubeAggregationFunction(self, CubeAggregationFunctionType.SUM)
        self._avg_op = CubeAggregationFunction(self, CubeAggregationFunctionType.AVG)
        self._median_op = CubeAggregationFunction(self, CubeAggregationFunctionType.MEDIAN)
        self._min_op = CubeAggregationFunction(self, CubeAggregationFunctionType.MIN)
        self._max_op = CubeAggregationFunction(self, CubeAggregationFunctionType.MAX)
        self._count_op = CubeAggregationFunction(self, CubeAggregationFunctionType.COUNT)
        self._stddev_op = CubeAggregationFunction(self, CubeAggregationFunctionType.STDDEV)
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
        """Returns the memory usage of the Cube in bytes."""
        df_memory = self._df.memory_usage(deep=True).sum()
        own_memory = self._getsize(self) - df_memory

        return df_memory + own_memory


    def _getsize(self, obj):
        """sum size of object & members."""
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

    def _name_of_object(self, obj):
        try:
            return obj.__name__
        except AttributeError:
            return id(obj)



    # endregion

    # region Data Access Methods
    def __getitem__(self, item):
        return self._evaluate(CubeAggregationFunctionType.SUM, item)

    def __setitem__(self, key, value):
        raise NotImplementedError("Not implemented yet")

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
        return isinstance(item, typing.List) or isinstance(item, typing.Tuple)

    def _evaluate(self, operation: CubeAggregationFunctionType, address):
        if not self._islist(address):
            address = [address,]

        # Process all arguments of the address
        measure = None          # the measure to be used for the operation
        unresolved_parts = []   # parts of the address that could not be resolved from dimensions
        row_mask: np.ndarray | None = None         # the mask to filter the rows of the dataframe
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
                            dimension = parts[0]
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

        if len(unresolved_parts) > 1:
            raise ValueError(f"Multiple unresolved member arguments found in address: {unresolved_parts}")

        if not measure:
            # Use the first measure as default if no measure is specified.
            measure = self._measures[0]

        # 2-step approach to get values to aggregate
        # First convert entire column to numpy array and then apply the mask.
        # This is slightly to much faster than applying the mask directly to the
        # dataframe by using: self._df.iloc[row_mask, measure_ordinal].to_numpy()
        values = self._df[measure.column].to_numpy()
        values: np.ndarray = values[row_mask]

        # Use numpy for the aggregation functions, slightly faster than Pandas
        match operation:
            case CubeAggregationFunctionType.SUM:
                return np.nansum(values)
            case CubeAggregationFunctionType.AVG:
                return np.nanmean(values)
            case CubeAggregationFunctionType.MEDIAN:
                return np.nanmedian(values)
            case CubeAggregationFunctionType.MIN:
                return np.nanmin(values)
            case CubeAggregationFunctionType.MAX:
                return np.nanmax(values)
            case CubeAggregationFunctionType.COUNT:
                return len(values)
            case CubeAggregationFunctionType.STDDEV:
                return np.nanstd(values)
            case CubeAggregationFunctionType.VAR:
                return np.nanvar(values)
            case CubeAggregationFunctionType.POF:
                return np.nansum(values) / self.df[measure].sum()
            case CubeAggregationFunctionType.NAN:
                return np.count_nonzero(np.isnan(values))
            case CubeAggregationFunctionType.AN:
                return np.count_nonzero(~np.isnan(values))
            case _:
                return None

    # endregion

class CubeAggregationFunction:
    """
    Internal helper class that represents an aggregation function, like SUM, MIN, MAX, VAG etc.,
    which are provided through the 'Cube' object, e.g. cube.sum[("A", "B", "C")].
    """
    def __init__(self, cube: Cube, operation: CubeAggregationFunctionType = CubeAggregationFunctionType.SUM):
        self._cube: Cube = cube
        self._op: CubeAggregationFunctionType = operation

    def __getitem__(self, item):
        return self._cube._evaluate(self._op, item)

    def __setitem__(self, key, value):
        raise NotImplementedError("Not implemented yet")


def cubed(df: pd.DataFrame, schema=None,
                 infer_schema_if_not_provided: bool = True, enable_caching: bool = True,
                 enable_write_back: bool = False) -> Cube:
        """
        Initializes a new Cube wrapping and providing a Pandas dataframe as a multi-dimensional data cube.
        The schema of the Cube can be either inferred automatically from the dataframe  (default) or defined explicitly.

        :param df: The Pandas dataframe to wrap into a Cube.
        :param schema: The schema of the Cube. If not provided, the schema will be inferred from the dataframe if
                parameter 'infer_schema_if_not_provided' is set to True.
        :param infer_schema_if_not_provided:  If True, the schema will be inferred from the dataframe if not provided.
        :param enable_caching: If True, intermediate results are cached for faster data access.
        :param enable_write_back: If True, the Cube will be writeable and changes to the data will be written back to the
                underlying dataframe.
        """
        return Cube(df, schema, infer_schema_if_not_provided, enable_caching, enable_write_back)