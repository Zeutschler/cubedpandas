import datetime
from abc import ABC
from typing import Iterable, Self
import numpy as np
from hybrid_dict import HybridDict
import pandas as pd

from pandas.api.types import (is_string_dtype, is_numeric_dtype, is_bool_dtype,
                              is_datetime64_any_dtype, is_timedelta64_dtype, is_categorical_dtype, is_object_dtype)

class Dimension(Iterable, ABC):
    """ Represents a measure of a cube."""
    def __init__(self, df: pd.DataFrame, column, enable_caching: bool = False):
        self._df: pd.DataFrame = df
        self._column = column
        self._column_ordinal = df.columns.get_loc(column)
        self._dtype = df[column].dtype
        self._members: set | None = None
        self._member_list: list | None = None
        self._enable_caching: bool = enable_caching
        self._cache: dict = {}
        self._counter: int = 0

    def _load_members(self):
        if self._members is None: # lazy loading
            self._member_list = self._df[self._column].unique().tolist()
            self._members = set(self._member_list)

    def contains(self, member):
        self._load_members()

        if isinstance(member, list) or isinstance(member, tuple):
            for m in member:
                if m not in self._members:
                    return False
            return True
        else:
            return member in self._members

    @property
    def members(self) -> list:
        self._load_members()
        return self._member_list

    @property
    def column(self):
        return self._column

    def count(self, member):
        return np.count_nonzero(self._resolve(member))

    def __len__(self):
        self._load_members()
        return len(self._member_list)

    def __eq__(self, other):
        return self._column == other

    def __hash__(self):
        return hash(str(self._column))

    def _resolve(self, member, row_mask = None)-> np.array:
        if isinstance(member, list):
            member = tuple(member)
        elif not isinstance(member, tuple):
            member = (member, )

        if row_mask is not None:
            if self._enable_caching:
                if member in self._cache:
                    mask = np.intersect1d(row_mask, self._cache[member])
                else:
                    mask = self._df.loc[:, self._column].isin(member)
                    mask = mask[mask == True].index.to_numpy()
                    self._cache[member] = mask
                    mask = np.intersect1d(row_mask, mask)
            else:
                mask = self._df.iloc[row_mask, self._column_ordinal].isin(member)
                mask = mask[mask == True].index.to_numpy()
        else:
            if self._enable_caching:
                if member in self._cache:
                    mask = self._cache[member]
                else:
                    mask = self._df.loc[:, self._column].isin(member)
                    mask = mask[mask == True].index.to_numpy()
                    self._cache[member] = mask
            else:
                mask = self._df.loc[:, self._column].isin(member)
                mask = mask[mask == True].index.to_numpy()
        return mask

    def __iter__(self) -> Self:
        self._load_members()
        self._counter = 0

        return self

    def __next__(self):
        if self._counter >= len(self.members):
            raise StopIteration
        member = self._member_list[self._counter]
        self._counter += 1
        return member