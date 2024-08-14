# CubedPandas - Copyright (c)2024 by Thomas Zeutschler, BSD 3-clause license, see file LICENSE included in this package.
import random
import sys
from fnmatch import fnmatch
from abc import ABC
from typing import Iterable, Self, Literal
import datetime
import numpy as np
import pandas as pd
from pandas.api.types import (is_string_dtype, is_numeric_dtype, is_bool_dtype,
                              is_datetime64_any_dtype, is_timedelta64_dtype,
                              is_categorical_dtype, is_object_dtype)

from cubedpandas.caching_strategy import CachingStrategy, EAGER_CACHING_THRESHOLD
from cubedpandas.date_parser import parse_date
from cubedpandas.statistics import DimensionStatistics
from cubedpandas.filter import Filter, FilterOperation, DimensionFilter, MeasureFilter


class Dimension(Iterable, ABC):
    """
    Represents a dimension of a cube, mapped to a column in the underlying Pandas dataframe.
    """

    def __init__(self, df: pd.DataFrame, column, caching: CachingStrategy = CachingStrategy.LAZY):
        """
        Initializes a new Dimension from a Pandas dataframe and a column name.
        """
        self._df: pd.DataFrame = df
        self._column = column
        self._column_ordinal = df.columns.get_loc(column)
        self._dtype = df[column].dtype
        self._members: set | None = None
        self._member_list: list | None = None
        self._member_array: np.ndarray | None = None
        self._cached: bool = False
        self._caching: CachingStrategy = caching
        self._cache: dict = {}
        self._cache_members: list | None = None
        self._counter: int = 0

    def __getattr__(self, name) -> Filter:
        """
        Dynamically resolves a Filter based on member names from the dimension. This enables a more natural
        access to the cube data using the Python dot notation.

        Member names need to be valid Python identifier/variable name. CubedPandas applies the following rules
        to resolve member names:
        - If a member name is also a valid Python identifier, it can be used directly. e.g., `Apple`
        - Member name resolving is case-insensitive, e.g., `apple` will resolve `Apple`.
        - White spaces in member names are replaced by underscores, e.g., `best_offer` will resolve `best offer`.
        - Leading numbers in a member name are replaced by underscores, e.g., `_2_cute` will resolve `2 cute`.
        - Leading and trailing underscores are ignored/removed, e.g., `hello` will resolve `    hello `.
        - All other special characters are removed, e.g., `12/4 cars` is the same as `124_cars`.

        - If the name is not a valid Python identifier (e.g. contains special characters), the `slicer`
        method needs to be used to resolve the member name. e.g., `12/4 cars` is a valid name for a value

        If the name is not a valid Python identifier (e.g. contains special characters), the `slicer`
        method needs to be used to resolve the member name. e.g., `12/4 cars` is a valid name for a value
        in a Pandas dataframe column, but not a valid Python identifier/variable name, hence `dimension["12/4 cars"]`
        needs to be used to return the member.


        Args:
            name: Name of a member or measure in the cube.

        Returns:
            A Cell object that represents the cube data related to the address.

        Samples:
            >>> cdf = cubed(df)
            >>> cdf.Online.Apple.cost
            50
        """
        return DimensionFilter(parent=self, expression=name)  #, dynamic_access=True)


    def _load_members(self):
        if self._member_array is None:
            values, counts = np.unique(self._df[self._column].to_numpy(), return_counts=True)
            self._member_array = values
            self._member_list = self._member_array.tolist()
            self._members = set(self._member_list)
        #if self._members is None:  # lazy loading
        #    self._member_list = self._df[self._column].unique().tolist()
        #    self._members = set(self._member_list)

    def _cache_warm_up(self, caching_threshold: int = EAGER_CACHING_THRESHOLD):
        """Warms up the cache of the Cube."""
        if self._caching < CachingStrategy.EAGER:
            return

        if caching_threshold < 1:
            caching_threshold = sys.maxsize

        self._load_members()

        if (((self._caching == CachingStrategy.EAGER) and (len(self._members) <= caching_threshold)) or
            (self._caching == CachingStrategy.FULL)) or (not self._cache_members is None):

            if self._cache_members is None:
                cache_members = self._members
            else:
                cache_members = self._cache_members

            for member in cache_members:
                mask = self._df.loc[:, self._column].isin([member, ])
                mask = mask[mask == True].index.to_numpy()
                self._cache[member] = mask

            self._cached = True

    def clear_cache(self):
        """Clears the cache of the Dimension."""
        self._cache = {}
        self._cached = False
        self._members = None
        self._member_list = None

    def contains(self, member):
        self._load_members()

        if isinstance(member, list) or isinstance(member, tuple):
            for m in member:
                if m not in self._members:
                    return False
            return True
        else:
            return member in self._members

    def filter(self, expression) -> DimensionFilter:
        """
        Returns a new DimensionFilter object based on the given expression.

        Args:
            expression: A member name or a valid filter expression.

        Returns:
            A new DimensionFilter object.
        """
        return DimensionFilter(self,expression)

    @property
    def df(self) -> pd.DataFrame:
        """
        Returns the underlying Pandas dataframe the dimension/column refers to.
        """
        return self._df

    @property
    def members(self) -> list:
        """
        Returns the list of members of the dimension.
        """
        self._load_members()
        return self._member_list

    @property
    def member_set(self) -> set:
        """
        Returns the set of members of the dimension.
        """
        self._load_members()
        return self._members

    @property
    def column(self):
        """
        Returns the column name in the underlying Pandas dataframe the dimension refers to.
        """
        return self._column

    @property
    def name(self):
        """
        Returns the name (column name in the underlying Pandas dataframe) of the dimension.
        """
        return self._column

    def count(self, member):
        """
        Returns the number of rows in the underlying dataframe where the dimension column contains the given member.
        """
        return np.count_nonzero(self._resolve(member))

    @property
    def dtype(self):
        """
        Returns the Pandas data type of the dimension column.
        """
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

    def _resolve_wildcard_members(self, members) -> list:
        if members == "*":
            return self.members
        else:
            if not isinstance(members, list | tuple):
                members = (members, )
            l1 = self.members
            l2 = set(members)
            matched_members = [x for x in l1 if any(fnmatch(x, p) for p in l2)]
            return matched_members

    def _resolve(self, member, row_mask=None) -> np.array:
        """
        Resolves a member or a list of members to a mask to filter the underlying dataframe.
        """
        if isinstance(member, Filter):
            return member.mask

        if isinstance(member, list):
            member = tuple(sorted(member)) # make sure the order is always the same, e.g. A,B == B,A
        if not isinstance(member, tuple):
            member = (member,)

        # 1. check if the member definition is already in the cache...
        if self._caching > CachingStrategy.NONE:
            if member in self._cache:
                if row_mask is None:
                    return self._cache[member]
                else:
                    # todo: maybe add faster intersection?
                    return np.intersect1d(row_mask, self._cache[member])

        # 2. ...if not, resolve the member(s)
        mask: np.ndarray | None = None
        for m in member:
            if mask is None:
                mask = self._resolve_member(m, row_mask)
            else:
                new_mask = self._resolve_member(m, row_mask)
                mask = np.union1d(mask, new_mask)
            if not len(mask):
                break

        # 3. cache the result
        if self._caching > CachingStrategy.NONE:
            self._cache[member] = mask

        if row_mask is None:
            return mask
        else:
            return np.intersect1d(row_mask, mask)

    def _check_exists_and_resolve_member(self, member,
                                         row_mask:np.ndarray | None = None,
                                         parent_member_mask:np.ndarray | None = None) \
            -> tuple[bool, np.ndarray | None, np.ndarray | None]:

        if self._caching > CachingStrategy.NONE:
            if member in self._cache:
                member_mask = self._cache[member]
                if not parent_member_mask is None:
                    member_mask = np.union1d(parent_member_mask, member_mask)

                if row_mask is None:
                    return True, member_mask, member_mask
                else:
                    return True, np.intersect1d(row_mask, member_mask), member_mask

        self._load_members()
        if not member in self._members:
            return False, None, None

        mask = self._df[self._column] == member
        member_mask = mask[mask == True].index.to_numpy()

        if self._caching > CachingStrategy.NONE:
            self._cache[member] = member_mask

        if not parent_member_mask is None:
            member_mask = np.union1d(parent_member_mask, member_mask)

        if row_mask is None:
            return True, member_mask, member_mask
        else:
            return True, np.intersect1d(row_mask, member_mask), member_mask


    def _resolve_member(self, member, row_mask=None) -> np.ndarray:
        # let's try to find the exact member
        mask = pd.Series([], dtype=pd.StringDtype())
        if is_string_dtype(self._dtype) and isinstance(member, str):
            mask = self._df[self._column] == member
        elif is_numeric_dtype(self._dtype) and isinstance(member, (int, float)):
            mask = self._df[self._column] == member
        elif is_bool_dtype(self._dtype) and isinstance(member, bool):
            mask = self._df[self._column] == member
        elif is_datetime64_any_dtype(self._dtype) and isinstance(member, (datetime.datetime, datetime.timedelta)):
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

    # region Random and statistics methods

    @property
    def statistics(self) -> DimensionStatistics:
        return DimensionStatistics(self)

    def choice(self):
        """
        Return a random member from the dimension.

        See https://docs.python.org/3/library/random.html#random.choice for more information.

        Returns:
            Return a random member from the dimension.
        """
        self._load_members()
        return random.choice(self._member_list)

    def choices(self, k:int=1, weights=None, cum_weights=None):
        """
        Return a `k` sized list of members chosen from the dimension (with replacement).

        See https://docs.python.org/3/library/random.html#random.choices for more information.

        Returns:
            Return a `k` sized list of members chosen from the dimension (with replacement).
        """
        self._load_members()
        return random.choices(self._member_list, weights=weights, cum_weights=cum_weights, k=k)

    def sample(self, k:int=1, counts=None):
        """
        Return a `k` sized list of unique members chosen from the dimension (without replacement).

        See https://docs.python.org/3/library/random.html#random.sample for more information.

        Returns:
            Return a `k` sized list of unique members chosen from the dimension (without replacement).
        """
        self._load_members()
        return random.sample(self._member_list, k=k, counts=counts)
    # endregion