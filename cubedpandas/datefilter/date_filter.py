from __future__ import annotations

import uuid
from collections.abc import Iterable
from datetime import datetime
from typing import Literal

from dateutil.parser import parserinfo

from cubedpandas.datefilter.base_parser import DateTextLanguageParser
from cubedpandas.datefilter.date_span import DateSpan


class DateFilter(Iterable[DateSpan]):
    """
    A date text parser for a specific language.
    As of now, only language `en` is supported.
    """

    def __init__(self, text: str | None = None, lang_iso_639_1: Literal["en"] = "en", raise_errors: bool = False):
        """
        Initializes a date text parser for the given language.

        Arguments:
            lang_iso_639_1: The ISO 639-1 2-digit language code for the language of the text to parse.
                Default is 'en' for English.
            raise_errors: If True, errors will be raised if the text cannot be parsed.
                If False, a (`None`, `None`) tuple will be returned in case of errors.
        """
        super().__init__()
        self._spans: list[DateSpan] = []
        self._message: str | None = None
        self._raise_errors: bool = raise_errors
        self._text: str | None = text
        self._iter_index = 0
        self._parser: DateTextLanguageParser | None = None
        try:
            self._parser = self._load_parser(lang_iso_639_1)
        except ImportError as e:
            raise ValueError(f"Parsing date text for language '{lang_iso_639_1}' is not supported. "
                             f"Failed to load and instance module/class '{self._modul_name(lang_iso_639_1)}'") from e

        if text is not None:
            self.parse(text)

    def __iter__(self):
        self._iter_index = -1
        return self

    def __next__(self):  # Python 2: def next(self)
        self._iter_index += 1
        if self._iter_index < len(self._spans):
            return self._spans[self._iter_index]
        raise StopIteration

    def __len__(self):
        return len(self._spans)

    def __getitem__(self, item):
        return self._spans[item]

    def _modul_name(self, language: str) -> str:
        """ Returns the expected module name for a given language."""
        return f'cubedpandas.datefilter.parser_{language}.DateTextParser'

    @property
    def language(self) -> str:
        """ Returns the ISO 639-1 language 2-difit code of the parser, e.g. 'en' for English."""
        return self._parser.language

    @property
    def message(self) -> str | None:
        """ Returns the last error message."""
        return self._message


    @property
    def raise_errors(self) -> bool:
        """ Returns True if errors will be raised if a text cannot be parsed."""
        return self._raise_errors

    @raise_errors.setter
    def raise_errors(self, value: bool):
        """ Sets if errors will be raised if a text cannot be parsed."""
        self._raise_errors = value

    def parse(self, text: str, parser_info: parserinfo | None = None) -> bool:
        """
            Parses and converts an arbitrary date- or time-related text into a (`datetime`, `datetime`) time-span tuple.
            If the text represents a single datetime then a (`datetime`, `None`) time-span tuple will be returned.
            If the text represents multiple time-spans or datetimes then a list of (`datetime`, `datetime`) time-span
            tuples will be return. If no date time can be resolved, (`None`, `None`) tuple will be returned.
            No error will be raised if the text cannot be parsed.

            Arguments:
                text: The text to parse, e.g. 'last month', 'next 3 days' or 'yesterday'.
                parser_info: (optional) A dateutil.parser.parserinfo instance to use for parsing the
                    text. If None, the default parser will be used.

            Returns:
                None | tuple[datetime, datetime | None] | list[tuple[datetime, datetime | None]] : The parsed time-span tuple(s).

            Examples:
                >>> parse('last month')  # if today would be in February 2024
                (datetime.datetime(2024, 1, 1, 0, 0), datetime.datetime(2024, 1, 31, 23, 59, 59, 999999))
            """
        self._message = None
        self._spans.clear()
        try:
            ds: DateSpan | list[DateSpan] = self._parser.parse(text, parser_info)
            if isinstance(ds, DateSpan):
                self._spans.append(ds)
            else:
                self._spans.extend(ds)
        except ValueError as e:
            self._message = str(e)
            if self._raise_errors:
                raise e
            return False
        return True

    def _load_parser(self, language: str) -> DateTextLanguageParser:
        """
        Loads the parser instance for the given language.
        It is expected that individual parsers are implemented in a module/class
        named 'cubedpandas.datetext.parser_{language}.DateTextParser'.
        """
        name = self._modul_name(language)
        components = name.split('.')
        mod = __import__(".".join(components[:-1]))
        for comp in components[1:]:
            mod = getattr(mod, comp)
        return mod()

    def to_sql(self, column: str, line_breaks: bool = False):
        """
        Converts the date spans representing the DateFilter into an ANSI-SQL compliant SQL fragment to be used
        for the execution of SQL queries.

        Arguments:
             column: The name of the SQL table column to filter.
             line_breaks: (optional) Flag if each date spans should be written in a separate line.

        """
        filters: list[str] = []
        column = column.strip()
        if " " in column and not column[0] in "['\"":
            column = f"[{column}]"
        for i, span in enumerate(self._spans):
            filters.append(f"({column} BETWEEN '{span.start.isoformat()}' AND '{span.end.isoformat()}')")
        if line_breaks:
            return " OR\n".join(filters)
        return " OR ".join(filters)

    def to_function(self, return_as_string: bool = False) -> callable | str:
        """
        Generate a compiled Python function that can be directly used as a filter function
        within Python, Pandas or other. The lambda function will return True if the input
        datetime is within the date spans of the DateFilter.

        Arguments:
            return_as_string: If True, the source code of the function will be returned as a string
                for code reuse. If False, the function will be returned as a callable Python function.

        Examples:
            >>> filter = DateFilter("today").to_function()
            >>> print(filter(datetime.now()))
            True

        """
        from types import FunctionType

        # prepare source
        func_name = f"filter_{str(uuid.uuid4()).lower().replace('-', '')}"
        filters: list[str] = [f"def {func_name}(x):", ]
        for i, span in enumerate(self._spans):
            s = span.start
            e = span.end
            if s.hour == 0 and s.minute == 0 and s.second == 0 and s.microsecond == 0 and s.microsecond == 0:
                start = f"datetime(year={s.year}, month={s.month}, day={s.day})"
            elif s.microsecond == 0:
                start = f"datetime(year={s.year}, month={s.month}, day={s.day}, hour={s.hour}, minute={s.minute}, second={s.second})"
            else:
                start = f"datetime(year={s.year}, month={s.month}, day={s.day}, hour={s.hour}, minute={s.minute}, second={s.second}, microsecond={s.microsecond})"
            end = f"datetime(year={e.year}, month={e.month}, day={e.day}, hour={e.hour}, minute={e.minute}, second={e.second}, microsecond={e.microsecond})"
            filters.append(f"\tif {start} <= x <= {end}:")
            filters.append(f"\t\treturn True")
        filters.append(f"\treturn False")

        source = f"\n".join(filters)
        if return_as_string:
            return source
        # compile
        f_code = compile(source, "<bool>", "exec")
        f_func = FunctionType(f_code.co_consts[0], globals(), "func_name")
        return f_func

    def to_lambda(self, return_as_string: bool = False) -> callable:
        """
        Generate a Python lambda function that can be directly used as a filter function
        within Python, Pandas or other. The lambda function will return True if the input
        datetime is within the date spans of the DateFilter.

        Arguments:
            return_as_string: If True, the source code of the lambda function will be returned as a string
                for code reuse. If False, the lambda function will be returned as a callable Python function.

        Examples:
            >>> filter = DateFilter("today").to_lambda()
            >>> print(filter(datetime.now()))
            True

        """

        # prepare source
        filters: list[str] = [f"lambda x :", ]
        for i, span in enumerate(self._spans):
            s = span.start
            e = span.end
            if s.hour == 0 and s.minute == 0 and s.second == 0 and s.microsecond == 0 and s.microsecond == 0:
                start = f"datetime(year={s.year}, month={s.month}, day={s.day})"
            elif s.microsecond == 0:
                start = f"datetime(year={s.year}, month={s.month}, day={s.day}, hour={s.hour}, minute={s.minute}, second={s.second})"
            else:
                start = f"datetime(year={s.year}, month={s.month}, day={s.day}, hour={s.hour}, minute={s.minute}, second={s.second}, microsecond={s.microsecond})"
            end = f"datetime(year={e.year}, month={e.month}, day={e.day}, hour={e.hour}, minute={e.minute}, second={e.second}, microsecond={e.microsecond})"
            if i > 0:
                filters.append(" or ")
            filters.append(f"{start} <= x <= {end}")

        source = f" ".join(filters)
        if return_as_string:
            return source
        # compile
        f_func = eval(source)
        return f_func

    def to_pd_lambda(self, return_as_string: bool = False) -> callable:
        """
        Generate a Python lambda function that can be directly applied to Pandas series (column) or
        to a 1d NumPy ndarray as a filter function. This allows the use of NumPy's internal vectorized functions.
        If applied to Pandas, the function will return a boolean Pandas series with the same length as the input series,
        if applied to a NumPy ndarray, the function will return a boolean array with the same length as the input array,
        where True indicates that the input datetime is within the date spans of the DateFilter.

        Arguments:
            return_as_string: If True, the source code of the Numpy lambda function will be returned as a string
                for code reuse. If False, the lambda function will be returned as a callable Python function.

        Examples:
            >>> data = np.array([datetime.now(), datetime.now()])
            >>> filter = DateFilter("today").to_numpy_lambda()
            >>> print(filter(data))
            [True, True]

        """

        # prepare source
        filters: list[str] = [f"lambda x :", ]
        for i, span in enumerate(self._spans):
            s = span.start
            e = span.end
            if s.hour == 0 and s.minute == 0 and s.second == 0 and s.microsecond == 0 and s.microsecond == 0:
                start = f"datetime(year={s.year}, month={s.month}, day={s.day})"
            elif s.microsecond == 0:
                start = f"datetime(year={s.year}, month={s.month}, day={s.day}, hour={s.hour}, minute={s.minute}, second={s.second})"
            else:
                start = f"datetime(year={s.year}, month={s.month}, day={s.day}, hour={s.hour}, minute={s.minute}, second={s.second}, microsecond={s.microsecond})"
            end = f"datetime(year={e.year}, month={e.month}, day={e.day}, hour={e.hour}, minute={e.minute}, second={e.second}, microsecond={e.microsecond})"
            if i > 0:
                filters.append(" | ")
            filters.append(f"((x >= {start}) & (x <= {end}))")

        source = f" ".join(filters)
        if return_as_string:
            return source
        # compile
        f_func = eval(source)
        return f_func
