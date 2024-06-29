from abc import abstractmethod
from enum import IntEnum
from typing import Any
import pandas as pd
import numpy as np

class MemberResolveStrategy(IntEnum):
    """
    Enumeration for the resolution strategy.
    """
    MATCH_ANY = 0
    MATCH_EXACT = 1
    MATCH_FUZZY = 2

class Resolver:
    """
    Base class for resolving member and column names to actual values within a dataframe.
    """

    def __init__(self):
        pass

    @property
    def primary(self) -> bool:
        """
        Indicates if the resolver should be used as a primary resolver. If `True` is returned, the resolver will
        be added as the primary=first resolver in the chain of built-in and/or custom resolvers. Any request
        to resolve a member name with matching criteria will be first routed this resolver.
        Please note that subsequently added resolvers that also return `True` will be placed before this resolver,
        so, order of adding custom resolvers may be important.

        If `False` is returned, the resolver will be added as a secondary=last resolver in the chain of built-in
        and/or custom resolvers. Default is `False`.
        :return:
        """
        return False

    @property
    def matching_types(self) -> None | list:
        """
        Returns the list of matching types that this resolver can handle. If `None` is returned, the resolver will be
        considered as a catch-all resolver and will be used for all matching types. Default is `None`.
        """
        return None

    @property
    def built_in(self) -> bool:
        """
        Indicates if the resolver is a built-in resolver.
        Built-in resolvers cannot be removed from the list of resolvers.
        Default is `False`.
        """
        return False


    @abstractmethod
    def resolve(self, df: pd.DataFrame, value, column: str | None = None,
                row_mask: np.ndarray | None = None,
                match_strategy: MemberResolveStrategy = MemberResolveStrategy.MATCH_ANY) -> (np.ndarray | None, Any):
        """
        Resolves a given value against the actual values within one, more or any column in a dataframe.

        Args:
            df:
                The dataframe to resolve the value in.
            value:
                The value to be resolved.
            column:
                The column to resolve the value in. If None, all columns will be considered.
            row_mask:
                A mask to filter the rows in the dataframe. If None, all rows will be considered.
                If a mask is provided, only the rows that are `True` in the mask will be considered.
            match_strategy:
                The strategy to be used for matching. Default is `MemberResolveStrategy.MATCH_ANY`, meaning
                that any match will be considered. If `MemberResolveStrategy.MATCH_EXACT` is used, only exact
                matches will be considered. If `MemberResolveStrategy.MATCH_FUZZY` is used, only fuzzy or advanced
                matches will also be considered.
        Returns:
            A Numpy array containing the indexes of the rows that match the value and optionally a default
            measure column name to be used for value aggregation. If no match can found, `(None, None)` will
            be returned.
        """
        return None, None
