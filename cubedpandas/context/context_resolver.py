from __future__ import annotations
from typing import TYPE_CHECKING
from collections.abc import Iterable
import datetime
import pandas as pd
import numpy as np

from context.datetime_resolver import resolve_datetime
from cubedpandas.context.context import Context
from context.expression import Expression


if TYPE_CHECKING:
    from cubedpandas.dimension import Dimension
    from cubedpandas.member import Member, MemberSet

class ContextResolver:
    """A helper class to resolve the address of a context."""

    @staticmethod
    def resolve(parent: Context, address, dynamic_attribute: bool = False,
                target_dimension: Dimension | None = None) -> Context:

        # 1. If no address needs to be resolved, we can simply return the current/parent context.
        if address is None:
            return parent

        # unpack the parent context
        cube = parent.cube
        row_mask = parent.row_mask
        member_mask = parent.member_mask
        measure = parent.measure
        dimension = parent.dimension

        # 2. If the address is already a context, then we can simply wrap it into a ContextContext and return it.
        if isinstance(address, Context):
            if parent.cube == address.cube:
                from cubedpandas.context.context_context import ContextContext
                return ContextContext(parent, address)
            raise ValueError(f"The context handed in as an address argument refers to a different cube/dataframe. "
                             f"Only contexts from the same cube can be used as address arguments.")

        # 3. String addresses are resolved by checking for measures, dimensions and members.
        if isinstance(address, str):

            # 3.1. Check for names of measures
            if address in cube.measures:
                from cubedpandas.context.measure_context import MeasureContext

                # set the measure for the context to the new resolved measure
                measure = cube.measures[address]
                resolved_context = MeasureContext(cube=cube, parent=parent, address=address, row_mask=row_mask,
                                                  measure=measure, dimension=dimension, resolve=False)
                return resolved_context
                # return ContextReference(context=resolved_context, address=address, row_mask=row_mask,
                #                        measure=measure, dimension=dimension)

            # 3.2. Check for names of dimensions
            if address in cube.dimensions:
                from cubedpandas.context.dimension_context import DimensionContext

                dimension = cube.dimensions[address]
                resolved_context = DimensionContext(cube=cube, parent=parent, address=address,
                                                    row_mask=row_mask,
                                                    measure=measure, dimension=dimension, resolve=False)
                return resolved_context
                # ref = ContextReference(context=resolved_context, address=address, row_mask=row_mask,
                #                       measure=measure, dimension=dimension)
                # return ref

            # 3.3. Check if the address contains a list of members, e.g. "A, B, C"
            address = ContextResolver.string_address_to_list(cube, address)

        # 4. Check for members of all data types over all dimensions in the cube
        #    Let's try start with a dimension that was handed in,
        #    if a dimension was handed in from the parent context.
        if not isinstance(address, list):

            skip_checks = False
            dimension_list = None
            dimension_switched = False

            # Check for dimension hints and leverage them, e.g. "products:apple", "children:1"
            if target_dimension is not None:
                dimension_list = [target_dimension]
            elif isinstance(address, str) and (":" in address):
                dim_name, member_name = address.split(":")
                if dim_name.strip() in cube.dimensions:
                    new_dimension = cube.dimensions[dim_name.strip()]
                    if dimension is not None:
                        dimension_switched = new_dimension != dimension
                    dimension = new_dimension

                    address = member_name.strip()  # todo: Datatype conversion required for int, bool, date?
                    dimension_list = [dimension]
                    skip_checks = True  # let's skip the checks as we have a dimension hint
            if dimension_list is None:
                dimension_list = cube.dimensions.starting_with_this_dimension(dimension)

            for dim in dimension_list:
                if dim == dimension and not dimension_switched:
                    # We are still at the dimension that was handed in, therefore we need to check for
                    # subsequent members from one dimension, e.g., if A, B, C are all members from the
                    # same dimension, then `cube.A.B.C` will require to join the member rows of A, B and C
                    # before we filter the rows from a previous context addressing another or no dimension.
                    if ContextResolver.matching_data_type(address, dim):
                        parent_row_mask = parent.get_row_mask(before_dimension=dimension)
                        exists, new_row_mask, member_mask = (
                            dimension._check_exists_and_resolve_member(address, parent_row_mask, member_mask,
                                                                       skip_checks=skip_checks))
                    else:
                        exists, new_row_mask, member_mask = False, None, None
                else:
                    # This indicates a dimension context switch,
                    # e.g. from `None` to dimension `A`, or from dimension `A` to dimension `B`.
                    exists, new_row_mask, member_mask = dim._check_exists_and_resolve_member(address, row_mask)

                if exists:
                    # We found the member...
                    from cubedpandas.member import Member, MemberSet
                    member = Member(dim, address)
                    members = MemberSet(dimension=dim, address=address, row_mask=new_row_mask,
                                        members=[member])
                    from cubedpandas.context.member_context import MemberContext
                    resolved_context = MemberContext(cube=cube, parent=parent, address=address,
                                                     row_mask=new_row_mask, member_mask=member_mask,
                                                     measure=measure, dimension=dim,
                                                     members=members, resolve=False)
                    return resolved_context

        if not dynamic_attribute:
            # As we are NOT in a dynamic context like `cube.A.online.sales`, where only exact measure,
            # dimension and member names are supported, and have not yet found a suitable member, we need
            # to check for complex member set definitions like filter expressions, list, dictionaries etc.
            is_valid_context, new_context_ref = ContextResolver.resolve_complex(parent, address, dimension)
            if is_valid_context:
                return new_context_ref
            else:
                if parent.cube.ignore_member_key_errors and not dynamic_attribute:
                    if dimension is not None:
                        if cube.df[dimension.column].dtype == pd.DataFrame([address, ])[0].dtype:
                            from cubedpandas.context.member_not_found_context import MemberNotFoundContext
                            return MemberNotFoundContext(cube=cube, parent=parent, address=address, dimension=dimension)

                raise ValueError(new_context_ref.message)

        # 4. If we've not yet resolved anything meaningful, then we need to raise an error...
        raise ValueError(f"Invalid member name or address '{address}'. "
                         f"Tip: check for typos and upper/lower case issues.")

    @staticmethod
    def resolve_complex(context: Context, address, dimension: Dimension | None = None) -> tuple[bool, Context]:
        """ Resolves complex member definitions like filter expressions, lists, dictionaries etc. """
        from cubedpandas.context.cube_context import CubeContext

        if dimension is None:
            dimension = context.dimension

        if isinstance(address, str):
            # 1. try wildcard expressions like "On*" > resolving e.g. to "Online"
            if "*" in address:
                if dimension is None:
                    if address == "*":
                        # This can only happen if we are still at the cube level, no dimension has been selected yet.
                        # In this case, we will return the cube context to return all records
                        return True, context
                    # We are at the cube level, so we need to consider all dimensions
                    dimensions = context.cube.dimensions
                else:
                    # We are at a dimension level, so we will only consider the current dimension
                    dimensions = [dimension]

                for dim in dimensions:
                    match_found, members = dim.wildcard_filter(address)

                    if match_found:
                        member_mask = None
                        parent_row_mask = context.get_row_mask(before_dimension=context.dimension)
                        exists, new_row_mask, member_mask = (
                            dim._check_exists_and_resolve_member(member=members, row_mask=parent_row_mask,
                                                                 parent_member_mask=member_mask,
                                                                 skip_checks=True))
                        if exists:
                            from cubedpandas.member import MemberSet
                            members = MemberSet(dimension=context.dimension, address=address, row_mask=new_row_mask,
                                                members=address)
                            from cubedpandas.context.member_context import MemberContext
                            resolved_context = MemberContext(cube=context.cube, parent=context, address=address,
                                                             row_mask=new_row_mask, member_mask=member_mask,
                                                             measure=context.measure, dimension=context.dimension,
                                                             members=members, resolve=False)
                            return True, resolved_context

            if dimension is not None and pd.api.types.is_datetime64_any_dtype(dimension.dtype):
                # 2. Date based filter expressions like "2021-01-01" or "2021-01-01 12:00:00"
                from_dt, to_dt = resolve_datetime(address)
                if (from_dt, to_dt) != (None, None):

                    # We have a valid date or data range, let's resolve it
                    from_dt, to_dt = np.datetime64(from_dt), np.datetime64(to_dt)
                    parent_row_mask = context.get_row_mask(before_dimension=context.dimension)
                    exists, new_row_mask, member_mask = dimension._check_exists_and_resolve_member(
                        member=(from_dt, to_dt), row_mask=parent_row_mask, parent_member_mask=context.member_mask,
                        skip_checks=True, evaluate_as_range=True)
                    if exists:
                        from cubedpandas.member import MemberSet
                        members = MemberSet(dimension=context.dimension, address=address, row_mask=new_row_mask,
                                            members=address)
                        from cubedpandas.context.member_context import MemberContext
                        resolved_context = MemberContext(cube=context.cube, parent=context, address=address,
                                                         row_mask=new_row_mask, member_mask=member_mask,
                                                         measure=context.measure, dimension=context.dimension,
                                                         members=members, resolve=False)
                        return True, resolved_context

            # 3. String based filter expressions like "sales > 100" or "A, B, C"
            #    Let's try to parse the address as a Python-compliant expression from the given address
            exp: Expression = Expression(address)
            try:
                if exp.parse():
                    # We have a syntactically valid expression, so let's try to resolve/evaluate it
                    exp_resolver = ExpressionContextResolver(context, address)
                    new_context = exp.evaluate(exp_resolver)

                    if new_context is None:
                        # We have a valid expression, but it did not resolve to a context
                        context.message = (f"Failed to resolve address or expression '{address}'. "
                                           f"Maybe it tries to refer to a member name that does not exist "
                                           f"in any of the dimension of the cube.")
                        return False, context

                    if isinstance(new_context, Iterable):
                        new_context = list(new_context)[-1]
                    return True, new_context

                else:
                    # Expression parsing failed
                    context.message = f"Failed to resolve address or expression '{address}."
                    return False, context

            except ValueError as err:
                context.message = f"Failed to resolve address or expression '{address}. {err}"
                return False, context


        elif isinstance(address, dict):

            # 4. Dictionary based expressions like {"product": "A", "channel": "Online"}
            #    which are only supported for the CubeContext.
            if not isinstance(context, CubeContext):
                context.message = (f"Invalid address "
                                   f"'{address}'. Dictionary based addressing is not "
                                   f"supported for contexts representing a dimensions, members or measures.")
                return False, context

            # process all arguments of the dictionary
            for dim_name, member in address.items():
                if dim_name not in context.cube.dimensions:
                    context.message = (f"Invalid address '{address}'. Dictionary key '{dim_name}' does "
                                       f"not reference to a dimension (dataframe column name) defined "
                                       f"for the cube.")
                    return False, context
                dim = context.cube.dimensions[dim_name]
                # first add a dimension context...
                from cubedpandas.context.dimension_context import DimensionContext
                context = DimensionContext(cube=context.cube, parent=context, address=dim_name,
                                           row_mask=context.row_mask,
                                           measure=context.measure, dimension=dim, resolve=False)
                # ...then add the respective member context.
                # This approach is required 1) to be able to properly rebuild the address and 2) to
                # be able to apply the list-based member filters easily.
                context = ContextResolver.resolve(context, member, target_dimension=dim)
            return True, context


        elif isinstance(address, Iterable):
            # 5. List based expressions like ["A", "B", "C"] or (1, 2, 3)
            #    Conventions:
            #    - When applied to CubeContext: elements can be measures, dimensions or members
            #    - When applied to DimensionContext: elements can only be members of the current dimension
            #    - When applied to MemberContext: NOT SUPPORTED
            #    - When applied to MeasureContext: NOT SUPPORTED
            from cubedpandas.context.dimension_context import DimensionContext
            if isinstance(context, DimensionContext):
                # For increased performance, no individual upfront member checks will be made.
                # Instead, we the list as a whole will processed by numpy.
                member_mask = None
                parent_row_mask = context.get_row_mask(before_dimension=context.dimension)
                exists, new_row_mask, member_mask = (
                    context.dimension._check_exists_and_resolve_member(member=address, row_mask=parent_row_mask,
                                                                       parent_member_mask=member_mask,
                                                                       skip_checks=True))
                if not exists:
                    context.message = (f"Invalid member list '{address}'. "
                                       f"At least one member seems to be an unsupported unhashable object.")
                    return False, context

                from cubedpandas.member import MemberSet
                members = MemberSet(dimension=context.dimension, address=address, row_mask=new_row_mask,
                                    members=address)
                from cubedpandas.context.member_context import MemberContext
                resolved_context = MemberContext(cube=context.cube, parent=context, address=address,
                                                 row_mask=new_row_mask, member_mask=member_mask,
                                                 measure=context.measure, dimension=context.dimension,
                                                 members=members, resolve=False)
                return True, resolved_context

            elif isinstance(context, CubeContext):
                # ...for CubeContext we need to check for arbitrary measures, dimensions and members.
                for item in address:
                    context = ContextResolver.resolve(context, item)
                return True, context

            else:
                # ...for MemberContext and MeasureContext and ContextContext we need to raise an error.
                context.message = (f"Invalid address '{address}'. List or tuple based addressing is not "
                                   f"supported for contexts representing members, measures or referenced contexts.")
                return False, context

        context.message = (f"Invalid member name or address '{address}'. "
                           f"Tip: check for typos and upper/lower case issues.")
        return False, context

    @staticmethod
    def string_address_to_list(cube, address: str):
        delimiter = cube.settings.list_delimiter
        if not delimiter in address:
            return address
        address = address.split(delimiter)
        return [a.strip() for a in address]

    @staticmethod
    def merge_contexts(parent: Context, child: Context) -> Context:
        """Merges the rows of two contexts."""

        if parent.dimension == child.dimension:
            parent_row_mask = parent.get_row_mask(before_dimension=parent.dimension)
            child._member_mask = np.union1d(parent.member_mask, child.member_mask)
            child._row_mask = np.intersect1d(parent_row_mask, child._member_mask, assume_unique=True)

        else:
            child._row_mask = np.intersect1d(parent.row_mask, child._member_mask, assume_unique=True)

        return child

    @staticmethod
    def matching_data_type(address: any, dimension: Dimension) -> bool:
        """Checks if the address matches the data type of the dimension."""
        if isinstance(address, str):
            return pd.api.types.is_string_dtype(dimension.dtype) # pd.api.types.is_object_dtype((dimension.dtype)
        elif isinstance(address, int):
            return pd.api.types.is_integer_dtype(dimension.dtype)
        elif isinstance(address, (str, datetime.datetime, datetime.date)):
            return pd.api.types.is_datetime64_any_dtype(dimension.dtype)
        elif isinstance(address, float):
            return pd.api.types.is_float_dtype(dimension.dtype)
        elif isinstance(address, bool):
            return pd.api.types.is_bool_dtype(dimension.dtype)
        return False


class ExpressionContextResolver:
    """A helper class to provide the current context to Expressions."""

    def __init__(self, context: Context, address):
        self._context: Context | None = context
        self._address = address

    @property
    def context(self):
        return self._context

    def resolve(self, name: str) -> Context | None:
        if name == self._address:
            return None
        # Please note that the context is changing/extended every time a new context is resolved.
        self._context = self._context[name]
        return self._context
