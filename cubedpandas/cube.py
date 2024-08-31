# CubedPandas - Copyright (c)2024, Thomas Zeutschler, see LICENSE file

from __future__ import annotations
import sys
from types import ModuleType, FunctionType
from gc import get_referents
from typing import Any
import pandas as pd

from cubedpandas.settings import CubeSettings
from cubedpandas.schema.schema import Schema
from cubedpandas.schema.measure_collection import MeasureCollection
from cubedpandas.schema.dimension import Dimension
from cubedpandas.schema.dimension_collection import DimensionCollection
from cubedpandas.ambiguities import Ambiguities
from cubedpandas.settings import CachingStrategy, EAGER_CACHING_THRESHOLD
from cubedpandas.context import Context, CubeContext, FilterContext
from cubedpandas.slice import Slice


class CubeLinks:
    def __init__(self, parent: Cube):
        self._parent: Cube = parent
        self._links: list[Cube] = []

    def __len__(self):
        return len(self._links)

    def __getitem__(self, index):
        return self._links[index]

    def add(self, cube: Cube):
        if not cube in self._links:
            self._links.append(cube)

    @property
    def parent(self) -> Cube:
        return self._parent

    @property
    def links(self) -> list[Cube]:
        return self._links

    @property
    def count(self) -> int:
        return len(self._links)


class Cube:
    """
    Wraps a Pandas dataframes into a cube to provide convenient multi-dimensional access
    to the underlying dataframe for easy aggregation, filtering, slicing, reporting and
    data manipulation and write back.
    A schema, that defines the dimensions and measures of the Cube, can either be
    inferred automatically from the underlying dataframe (default) or defined explicitly.
    """

    def __init__(self, df: pd.DataFrame,
                 schema=None,
                 exclude: str | list | tuple | None = None,
                 read_only: bool = True,
                 ignore_member_key_errors: bool = True,
                 ignore_case: bool = True,
                 ignore_key_errors: bool = True,
                 caching: CachingStrategy = CachingStrategy.LAZY,
                 eager_evaluation: bool = True,
                 ):
        """
        Wraps a Pandas dataframes into a cube to provide convenient multi-dimensional access
        to the underlying dataframe for easy aggregation, filtering, slicing, reporting and
        data manipulation and write back.

        Args:
            df:
                The Pandas dataframe to be wrapped into the CubedPandas `Cube` object.

            schema:
                (optional) A schema that defines the dimensions and measures of the Cube. If not provided, a
                default schema, treating all numerical columns will as measures, all other columns as dimensions,
                will be automatically inferred from the dataframe. If this behaviour is not desired, a valid
                schema must be provided. Default value is `None`.

            exclude:
                (optional) Defines the columns that should be excluded from the cube if no schema is provied.
                If a column is excluded, it will not be part of the schema and can not be accessed through the cube.
                Excluded columns will be ignored during schema inference. Default value is `None`.

            read_only:
                (optional) Defines if write backs to the underlying dataframe are permitted.
                If read_only is set to `True`, write back attempts will raise an `PermissionError`.
                If read_only is set to `False`, write backs are permitted and will be pushed back
                to the underlying dataframe.
                Default value is `True`.

            ignore_case:
                (optional) If set to `True`, the case of member names will be ignored, 'Apple' and 'apple'
                will be treated as the same member. If set to `False`, member names are case-sensitive,
                'Apple' and 'apple' will be treated as different members.
                Default value is `True`.

            ignore_key_errors:
                (optional) If set to `True`, key errors for members of dimensions will be ignored and
                cell values will return 0.0 or `None` if no matching record exists. If set to `False`,
                key errors will be raised as exceptions when accessing cell values for non-existing members.
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
                eargerly, if caching is set to `CacheStrategy.EAGER` or `CacheStrategy.FULL`. Above this
                threshold, the dimension will be cached lazily.
                Default value is `EAGER_CACHING_THRESHOLD`, equivalent to 256 unique members per dimension.

            eager_evaluation:
                (optional) If set to `True`, the cube will evaluate the context eagerly, i.e. when the context
                is created. Eager evaluation is recommended for most use cases, as it simplifies debugging and
                error handling. If set to `False`, the cube will evaluate the context lazily, i.e. only when
                the value of a context is accessed/requested.

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
        self._settings = CubeSettings()
        if not read_only is None:
            self._settings.read_only = read_only
            self._settings.ignore_member_key_errors = ignore_member_key_errors
            self._settings.ignore_case = ignore_case
            self._settings.ignore_key_errors = ignore_key_errors
            self._settings.eager_evaluation = eager_evaluation


        self._convert_values_to_python_data_types: bool = True
        self._df: pd.DataFrame = df
        self._exclude: str | list | tuple | None = exclude
        self._caching: CachingStrategy = caching
        self._caching_threshold: int = EAGER_CACHING_THRESHOLD
        self._member_cache: dict = {}
        self._cube_links = CubeLinks(self)
        self._runs_in_jupyter = Cube._runs_in_jupyter()

        # get or prepare the cube schema and setup dimensions and measures
        if schema is None:
            schema = Schema(df).infer_schema(exclude=self._exclude)
        else:
            schema = Schema(df, schema)
        self._schema: Schema = schema
        self._dimensions: DimensionCollection = schema.dimensions
        self._measures: MeasureCollection = schema.measures
        self._ambiguities: Ambiguities | None = None

        # warm up cache, if required
        if self._caching >= CachingStrategy.EAGER:
            self._warm_up_cache()

    # region Properties

    @property
    def settings(self) -> CubeSettings:
        """
        Returns:
            The settings of the Cube.
        """
        return self._settings

    @property
    def ambiguities(self) -> Ambiguities:
        """
        Returns:
            An Ambiguities object that provides information about ambiguous data types in the underlying dataframe.
        """
        if self._ambiguities is None:
            self._ambiguities = Ambiguities(self._df, self._dimensions, self._measures)
        return self._ambiguities

    # @property
    # def linked_cubes(self) -> CubeLinks:
    #     """
    #     Returns:
    #         A list of linked cubes that are linked to this cube.
    #     """
    #     # todo: implement a proper linked cubes collection object
    #     return self._cube_links

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
        self._member_cache = {}
        for dimension in self._dimensions:
            dimension.clear_cache()

    # endregion

    # region Data Access Methods
    @property
    def context(self) -> Context:
        context = CubeContext(self)
        return context

    def __getattr__(self, name) -> Context | CubeContext:
        """
        Dynamically resolves dimensions, measure or member from the cube.
        This enables a more natural access to the cube data using the Python dot notation.

        If the name is not a valid Python identifier and contains special characters or whitespaces
        or start with numbers, then the `slicer` method needs to be used to resolve the name,
        e.g., if `12 data %` is the name of a column or value in a dataframe, then `cube["12 data %"]`
        needs to be used to return the dimension, measure or column.

        Args:
            name: Existing Name of a dimension, member or measure in the cube.

        Returns:
            A Cell object that represents the cube data related to the address.

        Samples:
            >>> cdf = cubed(df)
            >>> cdf.Online.Apple.cost
            50
        """
        if name == "_ipython_canary_method_should_not_exist": # pragma: no cover
            raise AttributeError("cubedpandas")

        context = CubeContext(self, dynamic_attribute=True)

        if str(name).endswith("_"):
            name = str(name)[:-1]
            context = context[name]
            context = FilterContext(context)
            return context

        return context[name]

    def __getitem__(self, address: Any) -> Context:
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
        context = CubeContext(self)
        return context[address]

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
        if self.settings.read_only:
           raise PermissionError("Write back is not permitted on a read-only cube.")

        context = CubeContext(self)
        context[address].value = value

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
        raise NotImplementedError("Not implemented yet")
        # if self._read_only:
        #    raise PermissionError("Write back is not permitted on a read-only cube.")
        # dest_slice: Cell = Cell(self, address=address)
        # self._delete(dest_slice._row_mask)

    def slice(self, rows=None, columns=None, config=None) -> Slice:
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
        return CubeContext(self).slice(rows=rows, columns=columns, config=config)

    # endregion

    # region Dunder Methods
    def __str__(self):
        if self._runs_in_jupyter:
            return f"Jupyter Cube({len(self._df)} records, {len(self._dimensions)} dimensions, {len(self._measures)} measures)"
        else:
            return f"Cube({len(self._df)} records, {len(self._dimensions)} dimensions, {len(self._measures)} measures)"

    def __repr__(self):
        if self._runs_in_jupyter:
            from IPython.display import display
            display(f"Cube({len(self._df)} records, {len(self._dimensions)} dimensions, {len(self._measures)} measures)")
            display(self._df)
            return ""
        else:
            return f"Cube({len(self._df)} records, {len(self._dimensions)} dimensions, {len(self._measures)} measures)"
    # endregion

    # region Helper Methods
    @staticmethod
    def _runs_in_jupyter():
        """Returns True if the code runs in a Jupyter notebook, otherwise False."""
        return 'ipykernel' in sys.modules
    # endregion
