from typing import Iterable, Self


class CalmDict(Iterable):
    """A case-insensitive dictionary that does not raise KeyError when a key already exists."""

    def __init__(self, items: Iterable | None = None):
        cdict = {}
        for item in items:
            key = item
            if isinstance(item, str):
                key = key.strip().lower()
            cdict[key] = item
        self._dict: cdict


    def __iter__(self):
        self._counter = 0
        return self

    def __next__(self):
        if self._counter >= len(self):
            raise StopIteration
        key = list(self.keys())[self._counter]
        value = self[key]
        self._counter += 1
        return key, value

    def __getitem__(self, key):
        if isinstance(item, str):
            key = key.strip().lower()
        cdict[key] = item

        return super().__getitem__(key)

    def __setitem__(self, key, value):
        if key in self:
            raise KeyError(f"Key '{key}' already exists")

        super().__setitem__(key, value)