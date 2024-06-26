import pandas as pd
from cubedpandas.cube import Cube
from cubedpandas.caching_strategy import CachingStrategy, EAGER_CACHING_THRESHOLD


def cubed(df: pd.DataFrame, schema=None,
          infer_schema: bool = True,
          caching: CachingStrategy = CachingStrategy.LAZY,
          caching_threshold: int = EAGER_CACHING_THRESHOLD,
          read_only: bool = True):
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
    return Cube(df, schema, infer_schema, caching, caching_threshold, read_only)
