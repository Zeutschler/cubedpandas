# CubedPandas - Copyright (c)2024, Thomas Zeutschler, see LICENSE file

import pandas as pd

from cubedpandas.context.context import Context
from cubedpandas.cube import Cube
from cubedpandas.settings import CachingStrategy


@pd.api.extensions.register_dataframe_accessor("cubed")
class CubedPandasAccessor:
    """
    A Pandas extension that provides the CubedPandas 'cubed' accessor for Pandas dataframes.
    """

    def __init__(self, pandas_obj):
        self._validate(pandas_obj)
        self._df: pd.DataFrame = pandas_obj

    @staticmethod
    def _validate(df: pd.DataFrame):
        # Dataframe need to be non-empty
        if len(df) == 0:
            raise AttributeError("Method 'cubed' not provided for empty dataframe objects.")

    def __getattr__(self, item) -> Context:
        return Cube(self._df)[item]

    def __getitem__(self, address) -> Context:
        return Cube(self._df)[address]

    def __setitem__(self, address, value):
        Cube(self._df)[address] = value

    def __delitem__(self, address):
        del Cube(self._df)[address]

    @property
    def cube(self, schema=None,
             exclude: str | list | tuple | None = None,
             read_only: bool = True,
             ignore_member_key_errors: bool = True,
             ignore_case: bool = True,
             ignore_key_errors: bool = True,
             caching: CachingStrategy = CachingStrategy.LAZY):
        """
         Wraps a Pandas dataframes into a cube to provide convenient multi-dimensional access
        to the underlying dataframe for easy aggregation, filtering, slicing, reporting and
        data manipulation and write back.

        Arguments:

            schema:
                (optional) A schema that defines the dimensions and measures of the Cube. If not provided, the schema will be inferred from the dataframe if
                parameter `infer_schema` is set to `True`. For further details please refer to the documentation of the
                `Schema` class.
                Default value is `None`.

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

            ignore_member_key_errors:
                (optional) If set to `True`, key errors for members of dimensions will be ignored and
                cell values will return 0.0 or `None` if no matching record exists. If set to `False`,
                key errors will be raised as exceptions when accessing cell values for non-existing members.
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
                may also consume more memory. To cache all dimension members on
                initialization of the cube, set caching to `CachingStrategy.EAGER`.
                Please refer to the documentation of 'CachingStrategy' for more information.
                Default value is `CachingStrategy.LAZY`.


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
        """
        return Cube(df=self._df,
                    schema=schema,
                    exclude=exclude,
                    read_only=read_only,
                    ignore_member_key_errors=ignore_member_key_errors,
                    ignore_case=ignore_case,
                    ignore_key_errors=ignore_key_errors,
                    caching=caching)
