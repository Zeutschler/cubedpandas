from cubedpandas.resolvers.resolver import Resolver


class ResolversMeta(type):
    """Helper to implement singleton pattern for class Resolvers."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Resolvers(metaclass=ResolversMeta):
    """Provides and manages the member-name-resolvers available for to resolve member names."""

    def __init__(self):
        self._resolvers = {}

    def register(self, data_type, resolver:Resolver):
        if not isinstance(resolver, Resolver):
            raise ValueError(f"Resolver must be of type Resolver to get registered, not {type(resolver)}.")
        if data_type in self._resolvers:
            self._resolvers[data_type].append(resolver)
        else:
            self._resolvers[data_type] = [resolver, ]

    def unregister(self, resolver:Resolver):
        # please note that a single resolver can be registered multiple times for different data types.
        for resolvers in self._resolvers.values():
            if resolver in resolvers:
                resolvers.remove(resolver)

    def clear(self):
        """Removes all non-built-in resolvers from the list of resolvers."""
        for k, resolvers in self._resolvers.items():
            self._resolvers[k] = [r for r in resolvers if r.built_in]

    def __getitem__(self, item) -> list[Resolver]:
        return self._resolvers[item]


    def __str__(self):
        return f"CubedPandas Resolver, containing {self.__len__()} resolvers."

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return sum([len(v) for v in self._resolvers.values()])


