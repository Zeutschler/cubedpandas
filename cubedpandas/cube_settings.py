# CubedPandas - Copyright (c)2024 by Thomas Zeutschler, BSD 3-clause license, see LICENSE file.

class CubeSettings:

    def __init__(self):
        self._list_delimiter = ","
        self._auto_whitespace: bool = True
        self._read_only: bool = True
        self._convert_values_to_python_data_types: bool = True

    @property
    def list_delimiter(self):
        return self._list_delimiter

    @list_delimiter.setter
    def list_delimiter(self, value):
        self._list_delimiter = value


    @property
    def auto_whitespace(self):
        """
        Returns:
            `True`, if all measure-, dimension- and member-names containing whitespace
            can be written using underscores instead of a whitespace to support Python
            attribute naming conventions for dynamic access, e.g., `cdf.List_Price` will
            return the value of the measure column named 'List Price'.

            `False`, if the names must be written exactly as they are in the cube/dataframe,
            `cdf.List_Price` will return the value of the measure column named 'List_Price'

            Default is `True`.
        """
        return self._auto_whitespace

    @auto_whitespace.setter
    def auto_whitespace(self, value):
        """
        Returns:
            `True`, if all measure-, dimension- and member-names containing whitespace
            can be written using underscores instead of a whitespace to support Python
            attribute naming conventions for dynamic access, e.g., `cdf.List_Price` will
            return the value of the measure column named 'List Price'.

            `False`, if the names must be written exactly as they are in the cube/dataframe,
            `cdf.List_Price` will return the value of the measure column named 'List_Price'

            Default is `True`.
        """
        self._auto_whitespace = value

    @property
    def read_only(self) -> bool:
        """
        Returns:
            True if the Cube is read-only, otherwise False.
        """
        return self._read_only

    @read_only.setter
    def read_only(self, value: bool):
        """
        Sets the read-only status of the Cube.
        """
        self._read_only = value

    @property
    def convert_values_to_python_data_types(self) -> bool:
        """
        Returns:
            True if all values in the cube are converted to Python data types, otherwise False.
        """
        return self._convert_values_to_python_data_types

    @convert_values_to_python_data_types.setter
    def convert_values_to_python_data_types(self, value: bool):
        """
        Defines if all values in the cube are converted to Python data types.
        """
        self._convert_values_to_python_data_types = value
