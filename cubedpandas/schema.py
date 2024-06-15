# CubedPandas - Copyright (c)2024 by Thomas Zeutschler, BSD 3-clause license, see file LICENSE included in this package.

import json
from typing import Self, Any

import pandas as pd
from pandas.api.types import is_numeric_dtype

from cubedpandas.caching_strategy import CachingStrategy
from cubedpandas.dimension import Dimension
from cubedpandas.dimension_collection import DimensionCollection
from cubedpandas.measure import Measure
from cubedpandas.measure_collection import MeasureCollection


class Schema:
    """
    Defines a multidimensional schema, for cell-based data access to a Pandas dataframe using an Cube.

    The schema defines the dimensions and measures of the cube and can be either inferred from the underlying
    Pandas dataframe automatically or defined explicitly. The schema can be validated against the Pandas dataframe
    to ensure the schema is valid for the table.
    """

    def __init__(self, df: pd.DataFrame | None = None, schema: Self | Any = None, caching: CachingStrategy = CachingStrategy.LAZY):
        """
        Initializes a new schema for a Cube upon a given Pandas dataframe. If the dataframe is not provided,
        the schema needs to be built manually and can also not be validated against the Pandas dataframe.

        For building a schema manually, you can either create a new schema from scratch or you can load, extend
        and modify an existing schema as defined by parameter `schema`. The parameter `schema` can either be
        another Schema object, a Python dictionary containing valid schema information, a json string containing
        valid schema information or a file name or path to a json file containing valid schema information.

        :param df: (optional) the Pandas dataframe to build the schema from or for.
        :param schema: (optional) a schema to initialize the Schema with. The parameter `schema` can either be
                another Schema object, a Python dictionary containing valid schema information, a json string
                containing valid schema information or a file name or path to a json file containing valid schema
                information.
        :param caching: The caching strategy to be used for the Cube. Default is `CachingStrategy.LAZY`. Please refer to
                the documentation of 'CachingStrategy' for more information.
        """
        self._df: pd.DataFrame | None = df
        self._schema: Schema | Any = schema
        self._dimensions: DimensionCollection = DimensionCollection()
        self._measures: MeasureCollection = MeasureCollection()
        self._validation_message: str = ""
        self._caching: CachingStrategy = caching

        if schema is not None:
            if not self.validate(self._df):
                raise ValueError(self._validation_message)

    def validate(self, df: pd.DataFrame) -> bool:
        """
        Validates the schema against an existing Pandas dataframe.

        If returned True, the schema is valid for the given Pandas dataframe and can be used to access its data.
        Otherwise, the schema is not valid and will or may lead to errors when accessing its data.

        :param df: The Pandas dataframe to validate the schema against.

        :return: Returns True if the schema is valid for the given Pandas dataframe, otherwise False.
        """
        self._dimensions = DimensionCollection()
        for dimension in self._schema["dimensions"]:
            if "column" in dimension:
                column = dimension["column"]
                if column not in df.columns:
                    self._validation_message = f"Dimension column '{column}' not found in dataframe."
                    return False
                self._dimensions.add(Dimension(df, column, self._caching))
            else:
                if isinstance(dimension, str) or isinstance(dimension, int):
                    if dimension not in df.columns:
                        self._validation_message = f"Dimension column '{dimension}' not found in dataframe."
                        return False
                    self._dimensions.add(Dimension(df, dimension, self._caching))
                else:
                    self._validation_message = "Dimension column not found in schema."
                    return False

        self._measures = MeasureCollection()
        for measure in self._schema["measures"]:
            if "column" in measure:
                column = measure["column"]
                if column not in df.columns:
                    self._validation_message = f"Measure column '{column}' not found in dataframe."
                    return False
                self._measures.add(Measure(df, column))
            else:
                if isinstance(measure, str) or isinstance(measure, int):
                    if measure not in df.columns:
                        self._validation_message = f"Measure column '{measure}' not found in dataframe."
                        return False
                    self._measures.add(Measure(df, measure))
                else:
                    self._validation_message = "Measure column not found in schema."
                    return False
        return True

    @property
    def dimensions(self) -> DimensionCollection:
        """ Returns the dimensions of the schema."""
        return self._dimensions

    @property
    def measures(self) -> MeasureCollection:
        """ Returns the measures of the schema."""
        return self._measures

    def infer_schema(self, df: pd.DataFrame | None = None, columns: Any = None, sample_records: bool = False) -> Self:
        """
        Infers a multidimensional schema from the Pandas dataframe of the Schema or another Pandas dataframe by
        analyzing the columns of the table and their contents.

        This process can be time-consuming for large tables. For such cases, it is recommended to
        infer the schema only from a sample of the records by setting parameter 'sample_records' to True.
        By default, the schema is inferred from and validated against all records.

        The inference process tries to identify the dimensions and their hierarchies of the cube as
        well as the measures of the cube. If no schema cannot be inferred, an exception is raised.

        By default, string, datetime and boolean columns are assumed to be measure columns and
        numerical columns are assumed to be measures for cube computations. By default, all columns
        of the Pandas dataframe will be used to infer the schema. However, a subset of columns can be
        specified to infer the schema from. The subset needs to contain at least two columns, one
        for a single dimensions and one for a single measures.

        For more complex tables it is possible or even likely that the resulting schema does not match your
        expectations or requirements. For such cases, you will need to build your schema manually.
        Please refer the documentation for further details on how to build a schema manually.

        :param df: (optional) the Pandas dataframe to infer the schema from. If not provided, the schema
            is inferred from the Pandas dataframe the Schema object was initialized with.

        :param columns: (optional) a list of either column names or ordinal column ids to infer the schema from.

        :param sample_records: (optional) if True, the schema is inferred from a sample of records only.
            Setting 'sample_records' to True can be useful for large tables to speed up the inference process.
            By default, the schema is inferred from all records of the table.

        :return: Returns the inferred schema.
        """
        if df is None:
            df = self._df
        if df is None:
            return None

        schema = {"dimensions": [], "measures": []}
        self._dimensions = DimensionCollection()
        self._measures = MeasureCollection()
        for column_name, dtype in df.dtypes.items():
            if is_numeric_dtype(df[column_name]):
                schema["measures"].append({"column": column_name})
                self._measures.add(Measure(df, column_name))
            else:
                schema["dimensions"].append({"column": column_name})
                self._dimensions.add(Dimension(df, column_name, self._caching))

        return self

    # region Serialization
    @classmethod
    def from_dict(cls, dictionary: dict) -> Self:
        """
        Creates a new schema from a dictionary containing schema information for a Cube.
        Please refer to the documentation for further details on valid schema definitions.

        :param dictionary: The dictionary containing the schema information.
        :return: Returns a new schema object.
        :exception: Raises an exception if the schema information is not valid or incomplete.
        """
        return cls(schema=dictionary)

    @classmethod
    def from_json(cls, json_string: str) -> Self:
        """
        Creates a new schema from a json string containing schema information for a Cube.
        If the json string is not valid and does refer to a file that contains a valid schema in json format,
        an exception is raised.
        Please refer to the documentation for further details on valid schema definitions.

        :param json_string: The json string containing the schema information.
        :return: Returns a new schema object.
        :exception: Raises an exception if the schema information is not valid or incomplete.
        """
        return cls(schema=json_string)

    def to_dict(self) -> dict:
        """
        Converts the schema into a dictionary containing schema information for an Cube.

        :return: Returns a dictionary containing the schema information.
        """
        schema = {"dimensions": [], "measures": []}
        for measure in self._measures:
            schema["measures"].append({"column": measure.column})
        for dimension in self._dimensions:
            schema["dimensions"].append({"column": dimension.column})
        return schema

    def to_json(self) -> str:
        """
        Converts the schema into a dictionary containing schema information for an Cube.

        :return: Returns a dictionary containing the schema information.
        """
        return json.dumps(self.to_dict)

    def save_as_json(self, file_name: str):
        """
        Saves the schema as a json file.

        :param file_name: The name of the file to save the schema to.
        """
        with open(file_name, 'w') as file:
            json.dump(self.to_dict(), file)
    # endregion

    def __str__(self) -> str:
        return self.to_json()

    def __repr__(self) -> str:
        return self.to_json()

    def __len__(self):
        """ Returns the number of dimensions of the schema."""
        return len(self.dimensions)
