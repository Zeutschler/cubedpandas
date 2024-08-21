# CubedPandas - Copyright (c)2024, Thomas Zeutschler, see LICENSE file

import pandas as pd
from cubedpandas.cube import Cube
from cubedpandas.context.context import Context
from cubedpandas.settings import CachingStrategy, EAGER_CACHING_THRESHOLD


@pd.api.extensions.register_dataframe_accessor("cubed")
class CubedPandasAccessor:
    """
    A Pandas extension that provides the 'cubed' accessor to Pandas dataframes.
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
             infer_schema_if_not_provided: bool = True,
             caching: CachingStrategy = CachingStrategy.LAZY,
             caching_threshold: int = EAGER_CACHING_THRESHOLD,
             read_only: bool = True):
        """
        Initializes a new Cube wrapping and providing a Pandas dataframe as a multi-dimensional data cube.
        The schema of the Cube can be either inferred automatically from the dataframe  (default) or defined explicitly.

        :param schema: The schema of the Cube. If not provided, the schema will be inferred from the dataframe if
                parameter `infer_schema` is set to `True`.
        :param infer_schema_if_not_provided:  If True, the schema will be inferred from the dataframe if not provided.
        :param caching: The caching strategy to be used for the Cube. Default and recommended value for almost all use
                cases is `CachingStrategy.LAZY`, which caches dimension members on first access.
                Please refer to the documentation of 'CachingStrategy' for more information.
        :param caching_threshold: The threshold for EAGER caching. If the number of members in a dimension
                is below this threshold, the dimension will be cached eagerly.
                Default value is `EAGER_CACHING_THRESHOLD` := 256 members.
        :param read_only: If set to `False`, the Cube will become write-back enable and changes made to the data
                will be written to the underlying dataframe.
        """
        return Cube(df=self._df, schema=schema, infer_schema=infer_schema_if_not_provided, caching=caching,
                    caching_threshold=caching_threshold, read_only=read_only)
