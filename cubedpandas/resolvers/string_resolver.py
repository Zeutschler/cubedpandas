from typing import Any
import numpy as np
import pandas as pd

from cubedpandas.resolvers.resolver import Resolver, MemberResolveStrategy


class StringResolver(Resolver):

    def __init__(self):
        super().__init__()

    @property
    def primary(self) -> bool:
        return True

    @property
    def built_in(self) -> bool:
        return True

    @property
    def matching_types(self) -> list:
        return [str]

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
        if column:
            if match_strategy == MemberResolveStrategy.MATCH_EXACT:
                if value in df[column].unique():
                    return True, value
            else:
                for val in df[column].unique():
                    if value in val:
                        return True, val
        else:
            for col in df.columns:
                if match_strategy == MemberResolveStrategy.MATCH_EXACT:
                    if value in df[col].unique():
                        return True, value
                else:
                    for val in df[col].unique():
                        if value in val:
                            return True, val
        return False, value
