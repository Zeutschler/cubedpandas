# CubedPandas - Copyright (c)2024 by Thomas Zeutschler, BSD 3-clause license, see LICENSE file.

class CubeSettings:

    def __init__(self):
        self._list_delimiter = ","

    @property
    def list_delimiter(self):
        return self._list_delimiter

    @list_delimiter.setter
    def list_delimiter(self, value):
        self._list_delimiter = value
