import pandas as pd
from cubedpandas.cube import Cube
from cubedpandas.caching_strategy import CachingStrategy, EAGER_CACHING_THRESHOLD


def cubed(df: pd.DataFrame, schema=None,
          infer_schema_if_not_provided: bool = True,
          caching: CachingStrategy = CachingStrategy.LAZY,
          caching_threshold: int = EAGER_CACHING_THRESHOLD,
          enable_write_back: bool = False):
    """
    Initializes a new Cube wrapping and providing a Pandas dataframe as a multi-dimensional data cube.
    The schema of the Cube can be either inferred automatically from the dataframe  (default) or defined explicitly.

    Args:
        df:
            The Pandas dataframe to wrap into a Cube.

        schema:
            The schema of the Cube. If not provided, the schema will be inferred from the dataframe if
            parameter `infer_schema_if_not_provided` is set to `True`.

        infer_schema_if_not_provided:
            If True, the schema will be inferred from the dataframe if not provided. Default is True.
        caching:
            The caching strategy to be used for the Cube. Default and recommended value for almost all use
            cases is `CachingStrategy.LAZY`, which caches dimension members on first access.
            Please refer to the documentation of 'CachingStrategy' for more information.
        caching_threshold:
            The threshold as 'number of members' for EAGER caching. If the number of
            distinct members in a dimension is below this threshold, the dimension will be cached eargerly, if caching
            is set to CacheStrategy.EAGER or CacheStrategy.FULL. Above this threshold, the dimension will be cached
            lazily if caching is set to CacheStrategy.EAGER. For CacheStrategy.FULL this threshold is ignored.
            Default value is `EAGER_CACHING_THRESHOLD` 256 members.
        enable_write_back:
            If True, the Cube will become write-back enable and changes to the data
            will be written to the underlying dataframe. Default is False.

    Returns:
        A new Cube object that wraps the dataframe.

    Examples:
        >>> df = pd.value({"hello": [1, 2, 3]})
        >>> cdf = cubed(df)
        >>> cdf["*"]
        6
    """
    return Cube(df, schema, infer_schema_if_not_provided, caching, caching_threshold, enable_write_back)
