import datetime
import sys
from abc import ABC
from typing import Iterable, Self
import numpy as np
import pandas as pd

from cubedpandas.caching_strategy import CachingStrategy, EAGER_CACHING_THRESHOLD
from cubedpandas.dates import parse_date

from pandas.api.types import (is_string_dtype, is_numeric_dtype, is_bool_dtype,
                              is_datetime64_any_dtype, is_timedelta64_dtype, is_categorical_dtype, is_object_dtype)


class Dimension(Iterable, ABC):
    """ Represents a measure of a cube."""

    def __init__(self, df: pd.DataFrame, column, caching: CachingStrategy = CachingStrategy.LAZY):
        self._df: pd.DataFrame = df
        self._column = column
        self._column_ordinal = df.columns.get_loc(column)
        self._dtype = df[column].dtype
        self._members: set | None = None
        self._member_list: list | None = None
        self._cached: bool = False
        self._caching: CachingStrategy = caching
        self._cache: dict = {}
        self._cache_members: list | None = None
        self._counter: int = 0

    def _load_members(self):
        if self._members is None:  # lazy loading
            self._member_list = self._df[self._column].unique().tolist()
            self._members = set(self._member_list)

    def _cache_warm_up(self, caching_threshold: int = EAGER_CACHING_THRESHOLD):
        """Warms up the cache of the Cube."""
        if self._caching < CachingStrategy.EAGER:
            return

        if caching_threshold < 1:
            caching_threshold = sys.maxsize

        self._load_members()
        if (((self._caching == CachingStrategy.EAGER) and (len(self._members) <= caching_threshold)) or
            (self._caching == CachingStrategy.FULL)) or (not self._cache_members is None):

            if self._cache_members is not None:
                cache_members = self._cache_members
            else:
                cache_members = self._members

            for member in cache_members:
                mask = self._df.loc[:, self._column].isin([member, ])
                mask = mask[mask == True].index.to_numpy()
                self._cache[member] = mask

            self._cached = True

    def clear_cache(self):
        """Clears the cache of the Dimension."""
        self._cache = {}

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

    @property
    def dtype(self):
        return self._dtype

    def __len__(self):
        self._load_members()
        return len(self._member_list)

    def __eq__(self, other):
        return self._column == other

    def __hash__(self):
        return hash(str(self._column))

    def __str__(self):
        return self._column

    def __repr__(self):
        return self._column

    def _resolve(self, member, row_mask=None) -> np.array:
        if isinstance(member, list):
            member = tuple(member)
        if not isinstance(member, tuple):
            member = (member,)

        # 1. check if the member definition is already in the cache...
        if self._caching > CachingStrategy.NONE:
            if member in self._cache:
                # return self._cache[member]
                if row_mask is None:
                    return self._cache[member]
                else:
                    return np.intersect1d(row_mask, self._cache[member])

        # 2. ...if not, resolve the member(s)
        mask: np.ndarray | None = None
        for m in member:
            if mask is None:
                mask = self._resolve_member(m, row_mask)
            else:
                mask = np.union1d(mask, self._resolve_member(m, row_mask))
            if not len(mask):
                break

        # 3. cache the result
        if self._caching > CachingStrategy.NONE:
            self._cache[member] = mask

        if row_mask is None:
            return mask
        else:
            return np.intersect1d(row_mask, mask)

    def _resolve_member(self, member, row_mask=None) -> np.ndarray:

        # let's try to find the exact member
        mask = self._df[self._column] == member
        mask = mask[mask == True].index.to_numpy()

        if len(mask) == 0:
            # no direct match found, so...
            # ...depending on the data types of member and dimension column,
            # we test other ways to resolve the member.
            if isinstance(member, str):

                if is_datetime64_any_dtype(self._dtype):
                    # for datetime dimension (and member is string), try to parse the string as a date or date range
                    mask = np.array([])
                    first_date, last_date = parse_date(member)
                    if first_date is not None:
                        if last_date is None:
                            # a single date was returned
                            mask = self._df[self._column] == member
                            mask = mask[mask == True].index.to_numpy()
                        else:
                            # a date range (2 datetime values, first and last) was returned
                            mask = self._df.loc[:, self._column].between(first_date, last_date)
                            mask = mask[mask == True].index.to_numpy()
                    else:
                        # a valid date could not be parsed
                        mask = np.array([])

        return mask

    def _resolve_old(self, member, row_mask=None) -> np.array:
        if isinstance(member, list):
            member = tuple(member)
        elif not isinstance(member, tuple):
            member = (member,)

        if row_mask is not None:
            if self._caching > CachingStrategy.NONE:
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
            if self._caching > CachingStrategy.NONE:
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
