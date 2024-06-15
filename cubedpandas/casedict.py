# CubedPandas - Copyright (c)2024 by Thomas Zeutschler, BSD 3-clause license, see file LICENSE included in this package.

class CaseDict(dict):
    """
    A dictionary that allows case-insensitive access.
    """
    def __init__(self, iterable, case_sensitive=True):
        super().__init__(iterable)
        self._case_sensitive = case_sensitive
        self._lower_keys = {k.lower(): k for k in self.keys()}

    @property
    def case_sensitive(self) -> bool:
        """Returns True if the dictionary is case-sensitive, False otherwise."""
        return self._case_sensitive

    @case_sensitive.setter
    def case_sensitive(self, value: bool):
        """Switches the case sensitivity of the dictionary on or off."""
        self._case_sensitive = value

    def __getattr__(self, key):
        if self._case_sensitive and isinstance(key, str):
            return self[self._lower_keys[key.lower()]]
        return self[key]

    def __setattr__(self, key, value):
        if self._case_sensitive and isinstance(key, str):
            self._lower_keys[key.lower()] = key
        self[key] = value

    def __delattr__(self, key):
        if self._case_sensitive and isinstance(key, str):
            del self[self._lower_keys[key.lower()]]
        else:
            del self[key]

    def __contains__(self, key):
        if self._case_sensitive and isinstance(key, str):
            return key.lower() in self._lower_keys
        return super().__contains__(key)
