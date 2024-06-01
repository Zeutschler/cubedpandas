
from __future__ import annotations

from collections.abc import Iterable
from typing import SupportsFloat
import typing
# noinspection PyProtectedMember

if typing.TYPE_CHECKING:
    import cube as _cube


class Slice(SupportsFloat):
    """
    A slice represents a multi-dimensional data cell or data area in a cube. Slice objects can
    be used to navigate through and interact with the data space of a cube and the underlying dataframe.
    Slices behave like float values and can be directly used in mathematical calculations that read from
    or write to a cube.

    Sample usage:

    .. code:: python
        import cubedpandas as cpd

        df = get_your_dataframe()
        cube = cpd.Cube(df)

        # get a value from the cube and add 19% VAT
        net_value = cube.slice("2024", "Aug", "Germany", "NetSales")
        gross_sales_usa = net_value * 1.19

        # create new data or overwrite data for 2025 by copying all 2024 prices and adding 5% inflation
        cube.slice("2025", "Price") = cube.slice("2024", "Price") * 1.05
    """

    __slots__ = "_cube", "_names", "_dim_count", "_address", "_bolt"

    #: Indicates that either subsequent rules should continue and do the calculation
    #: work or that the cell value, either from a base-level or an aggregated cell,
    #: form the underlying cube should be used.
    CONTINUE = object()
    #: Indicates that rules function was not able return a proper result (why ever).
    NONE = object()
    #: Indicates that the rules functions run into an error. Such errors will be
    #: pushed up to initially calling cell request.
    ERROR = object()

    #: Indicates that the rules functions wants to bypass all rules and get the
    #: underlying base_level or aggregated value from the cube.
    BYPASS_RULES = object()

    # region Initialization
    @classmethod
    def create(cls, cube, names, address, bolt):
        slice = Slice()
        slice._cube = cube
        slice._names = names
        slice._dim_count = len(names)
        slice._address = address
        slice._bolt = bolt
        return slice

    def __init__(self):
        self._cube = None
        self._names = None
        self._address = None
        self._bolt = None
        self._dim_count = -1

    def __new__(cls):
        return SupportsFloat.__new__(cls)

    # endregion

    # region Properties
    @property
    def value(self):
        """Reads the value of the current cell idx_address from the underlying cube."""
        return self._cube._get(self._bolt)

    @value.setter
    def value(self, value):
        """Writes a value of the current cell idx_address to the underlying cube."""
        self._cube._set(self._bolt, value)

    @property
    def numeric_value(self) -> float:
        """Reads the numeric value of the current cell idx_address from the underlying cube."""
        value = self._cube._get(self._bolt)
        if isinstance(value, (int, float, complex)) and not isinstance(value, bool):
            return float(value)
        else:
            return 0.0


    @property
    def cube(self) -> _cube.Cube:
        """Returns the cube the cell belongs to."""
        return self._cube

    # endregion

    # region methods
    def alter(self, *args) -> Slice:
        """
        Creates a modified copy of a Slice object.

        :param args: One or more modifiers (member names) for at least one dimension of the cube.
            Member names can be in one of the ƒollowing formats:

               {member} e.g.: clone = c.alter("Mar", ...)
               {cube_name:member} e.g.: clone = c.alter("months:Mar", ...)
               {dimension_index:member} e.g.: clone = c.alter("1:Mar", ...)

            If multiple modifiers for a single dimension are defined, then the last of those will be used.
        :return: A new Slice object.
        """
        modifiers = []

        # super_level, idx_address, idx_measure = self._bolt
        super_level, idx_address = self._bolt
        idx_address = list(idx_address)
        address = list(self._address)

        for member in args:
            if isinstance(member, mod_member.Member):
                # The easy way! The Member object should be properly initialized already.
                raise NotImplementedError("Working on that...")

            elif isinstance(member, str):
                idx_dim, idx_member, member_level, member_name = self._get_member(member)
                member_def = self._cube._dimensions[idx_dim]._defs.idx_lookup[idx_member]
                address[idx_dim] = member_def.name

                # adjust the super_level
                member_def = self._cube._dimensions[idx_dim]._defs.idx_lookup[self._bolt[1][idx_dim]]
                super_level -= member_def.level
                super_level += member_level

                modifiers.append((idx_dim, idx_member))
            else:
                raise TypeError(f"Invalid type '{type(member)}'. Only type 'str' and 'Member are supported.")

        for modifier in modifiers:
            idx_address[modifier[0]] = modifier[1]
        # bolt = (super_level, tuple(idx_address), idx_measure)
        bolt = (super_level, tuple(idx_address))
        return Slice.create(self._cube, self._names, address, bolt)

    def member(self, dimension_and_or_member_name: str) -> mod_member.Member:
        """
        Create a new Member object from the Cell's current context.
        This can be either the current member of a specific dimension,
        if called with a dimension name, e.g., ``c.member("months")`` .
        Or it can be already a modified member of a dimension, if called
        with a member name, e.g., ``c.member("months:Jul")`` .

        :param dimension_and_or_member_name: Name of the dimension and or member to be returned.

        .. code:: python

            cell = cube.cell("2022", "Jan", "North", "Sales")
            jan = c.member("months")
            jul = c.member("months:Jul")
            jul = c.member("1:Aug")  # 'months' is the second dimension of the cube, so zero-based index is 1.

        :return: A new Member object.
        """
        idx_dim, idx_member, member_level, member_name = self._get_member(dimension_and_or_member_name)
        member_def = self._cube._dimensions[idx_dim]._defs[member_name]
        member = mod_member.Member(member_def, self._cube)
        return member

    # endregion

    # region Cell manipulation via indexing/slicing
    def __getitem__(self, args):
        if not args:
            value = self._cube._get(self._bolt)
        elif not isinstance(args, (str, mod_member.Member)) and (args[-1] == self.BYPASS_RULES):
            return self._cube._get(self.__item_to_bolt(args[:len(args) - 1]), True)
        else:
            value = self._cube._get(self.__item_to_bolt(args))
        if value is None:
            return 0.0  # Rules need numeric values
        else:
            return value
            # return self._cube._get(self.__item_to_bold(args))

    def __setitem__(self, args, value):
        if args:
            self._cube._set(self.__item_to_bolt(args), value)
        else:
            self._cube._set(self._bolt, value)

    def __delitem__(self, args):
        self.__setitem__(args, None)

    # endregion

    # region - Dynamic attribute resolving
    def __getattr__(self, name):
        name = str(name).replace("_", " ")
        return self.__getitem__(name)

    # def __getattribute__(*args):
    #     print("Class getattribute invoked")
    #     return object.__getattribute__(*args)
    # endregion

    # region Cell manipulation
    def __item_to_bolt(self, item):
        """Setting a value through indexing/slicing will temporarily modify the cell address and return
        the value from that cell idx_address. This does NOT modify the cell address of the Cell object.
        To modify the cell address of a Cell, you can call the ``.alter(...)`` method."""

        modifiers = []
        if isinstance(item, str) or not isinstance(item, Iterable):
            item = (item,)

        # super_level, idx_address, idx_measure = self._bolt
        super_level, idx_address = self._bolt
        idx_address = list(idx_address)

        for member in item:
            if isinstance(member, mod_member.Member):
                member_def = self._cube._dimensions[member.dim_index]._defs.idx_lookup[self._bolt[1][member.dim_index]]

                super_level -= member_def.level
                super_level += member.level
                modifiers.append((member.dim_index, member.index))

            elif isinstance(member, str):
                idx_dim, idx_member, member_level, member_name = self._get_member(member)
                member_def = self._cube._dimensions[idx_dim]._defs.idx_lookup[self._bolt[1][idx_dim]]

                super_level -= member_def.level
                super_level += member_level

                modifiers.append((idx_dim, idx_member))
            elif member is Ellipsis:
                # support for 3-dot ellipsis notation e.g. 'cell[...]' to enable self-referencing the current cell
                continue
            else:
                raise TypeError(f"Invalid type '{type(member)}'. Only type 'str' and 'Member are supported.")

        # Finally modify the idx_address and set the value
        for modifier in modifiers:
            idx_address[modifier[0]] = modifier[1]
        # bolt = (super_level, tuple(idx_address), idx_measure)
        bolt = (super_level, tuple(idx_address))
        return bolt

    def _get_member(self, member):
        # The hard way! We need to evaluate where the member is coming from
        # Convention: member names come in one of the following formats:
        #   c["Mar"] = 333.0
        #   c["months:Mar"] = 333.0
        #   c["1:Mar"] = 333.0

        dimensions = self._cube._dimensions
        idx_dim = -1
        pos = member.find(":")
        if pos != -1:
            # lets extract the dimension name and check if it is valid, e.g., c["months:Mar"]
            name = member[:pos].strip()

            # special test for ordinal dim position instead of dim name, e.g., c["1:Mar"] = 333.0
            if name.isdigit():
                ordinal = int(name)
                if 0 <= ordinal < len(self._names):
                    # that's a valid dimension position number
                    idx_dim = ordinal
            if idx_dim == -1:
                if name not in self._cube._dim_lookup:
                    raise mod_exceptions.TinyOlapInvalidAddressError(f"Invalid member key. '{name}' is not a dimension "
                                                                     f"in cube '{self._cube.name}. Found in '{member}'.")
                idx_dim = self._cube._dim_lookup[name]

            # adjust the member name
            member = member[pos + 1:].strip()
            member_def = dimensions[idx_dim]._defs.get(member, None)

            if not member_def:
                raise mod_exceptions.TinyOlapInvalidAddressError(f"Invalid member key. '{member}'is not a member of "
                                                                 f"dimension '{name}' in cube '{self._cube.name}.")
            idx_member = member_def.idx
            member_level = member_def.level
            member_name = member_def.name

            return idx_dim, idx_member, member_level, member_name

        # No dimension identifier in member name, search all dimensions
        # ...we'll search in reverse order, as we assume that it is more likely,
        #    that inner dimensions are requested through rules. Although this might be a wrong assumption.
        for idx_dim in range(self._dim_count - 1, -1, -1):
            member_def = dimensions[idx_dim]._defs.get(member, None)
            if member_def:
                idx_member = member_def.idx
                member_level = member_def.level
                member_name = member_def.name
                return idx_dim, idx_member, member_level, member_name

        # Still nothing found ? Then it might be just a dimension name or dimension ordinal
        # to reference the current member of that dimension.
        name = member
        # special test for ordinal dim position instead of dim name, e.g., c["1:Mar"] = 333.0
        if isinstance(name, int) or name.isdigit():
            ordinal = int(name)
            if 0 <= ordinal < len(self._names):
                # that's a valid dimension position number
                idx_dim = ordinal
            if idx_dim == -1:
                if name not in self._cube._dim_lookup:
                    raise mod_exceptions.TinyOlapInvalidAddressError(f"Invalid member key. '{name}' is not a dimension "
                                                                     f"in cube '{self._cube.name}. Found in '{member}'.")
                idx_dim = self._cube._dim_lookup[name]

            idx_member = self._bolt[1][idx_dim]
            member_def = dimensions[idx_dim]._defs.idx_lookup.get(idx_member, None)
            member_level = member_def.level
            member_name = member_def.name
            return idx_dim, idx_member, member_level, member_name
        else:
            idx_dim = self._cube._get_dimension_ordinal(name)
            if idx_dim > -1:
                idx_member = self._bolt[1][idx_dim]
                member_def = dimensions[idx_dim]._defs.idx_lookup.get(idx_member, None)
                member_level = member_def.level
                member_name = member_def.name
                return idx_dim, idx_member, member_level, member_name

        # You loose, member does not seem to exist...
        if idx_dim == -1:
            raise KeyError(f"'{member}' is not a member of any dimension in "
                           f"cube '{self._cube.name}', or a valid reference to any of it's dimensions.")

    # endregion

    # region operator overloading and float behaviour
    def __float__(self) -> float:  # type conversion to float
        return self.numeric_value

    def __index__(self) -> int:  # type conversion to int
        return int(self.numeric_value)

    def __neg__(self):  # - unary operator
        return - self.numeric_value

    def __pos__(self):  # + unary operator
        return self.numeric_value

    def __add__(self, other):  # + operator
        return self.numeric_value + other

    def __iadd__(self, other):  # += operator
        return self.numeric_value + other.numeric_value

    def __radd__(self, other):  # + operator
        return other + self.numeric_value

    def __sub__(self, other):  # - operator
        return self.numeric_value - other

    def __isub__(self, other):  # -= operator
        return self.numeric_value - other

    def __rsub__(self, other):  # - operator
        return other - self.numeric_value

    def __mul__(self, other):  # * operator
        return self.numeric_value * other

    def __imul__(self, other):  # *= operator
        return self.numeric_value * other

    def __rmul__(self, other):  # * operator
        return self.numeric_value * other

    def __floordiv__(self, other):  # // operator (returns an integer)
        return self.numeric_value // other

    def __ifloordiv__(self, other):  # //= operator (returns an integer)
        return self.numeric_value // other

    def __rfloordiv__(self, other):  # // operator (returns an integer)
        return other // self.numeric_value

    def __truediv__(self, other):  # / operator (returns an float)
        return self.numeric_value / other

    def __idiv__(self, other):  # /= operator (returns an float)
        return self.numeric_value / other

    def __rtruediv__(self, other):  # / operator (returns an float)
        return other / self.numeric_value

    def __mod__(self, other):  # % operator (returns a tuple)
        return self.numeric_value % other

    def __imod__(self, other):  # %= operator (returns a tuple)
        return self.numeric_value % other

    def __rmod__(self, other):  # % operator (returns a tuple)
        return other % self.numeric_value

    def __divmod__(self, other):  # div operator (returns a tuple)
        return divmod(self.numeric_value, other)

    def __rdivmod__(self, other):  # div operator (returns a tuple)
        return divmod(other, self.numeric_value)

    def __pow__(self, other, modulo=None):  # ** operator
        return self.numeric_value ** other

    def __ipow__(self, other, modulo=None):  # **= operator
        return self.numeric_value ** other

    def __rpow__(self, other, modulo=None):  # ** operator
        return other ** self.numeric_value

    def __lt__(self, other):  # < (less than) operator
        return self.numeric_value < other

    def __gt__(self, other):  # > (greater than) operator
        return self.numeric_value > other

    def __le__(self, other):  # <= (less than or equal to) operator
        return self.numeric_value <= other

    def __ge__(self, other):  # >= (greater than or equal to) operator
        return self.numeric_value >= other

    def __eq__(self, other):  # == (equal to) operator
        return self.numeric_value == other

    def __and__(self, other):  # and (equal to) operator
        return self.numeric_value and other

    def __iand__(self, other):  # and (equal to) operator
        return self.numeric_value and other

    def __rand__(self, other):  # and (equal to) operator
        return other and self.numeric_value

    def __or__(self, other):  # or (equal to) operator
        return self.numeric_value or other

    def __ior__(self, other):  # or (equal to) operator
        return self.numeric_value or other

    def __ror__(self, other):  # or (equal to) operator
        return other or self.numeric_value

    # endregion

    # region conversion function
    def __abs__(self):
        return self.numeric_value.__abs__()

    def __bool__(self):
        return self.numeric_value.__bool__()

    def __str__(self):
        return self.value.__str__()

    def __int__(self):
        return self.numeric_value.__int__()

    def __ceil__(self):
        return self.numeric_value.__ceil__()
    # endregion
