from __future__ import annotations

from typing import Literal, LiteralString, TypeAlias
from datetime import datetime
from dateutil.parser import parserinfo
from cubedpandas.datetext.base_parser import DateTextLanguageParser


def parse(text: str, lang_iso_639_1: Literal["en"] = "en", raise_errors: bool = False) \
        -> (tuple[datetime | None, datetime | None] |
            list[tuple[datetime | None, datetime | None]]):
    """
    Parses and converts an arbitrary date- or time-related text into a (`datetime`, `datetime`) time-span tuple.
    If the text represents a single datetime then a (`datetime`, `None`) time-span tuple will be returned.
    If the text represents multiple time-spans or datetimes then a list of (`datetime`, `datetime`) time-span
    tuples will be return. If no date time can be resolved, (`None`, `None`) tuple will be returned.
    No error will be raised if the text cannot be parsed.

    As of now, only language `en` is supported.

    Arguments:
        text: The text to parse, e.g. 'last month', 'next 3 days' or 'yesterday'.

        lang_iso_639_1: (optional) The ISO 639-1 2-digit language code for the language of the text to parse.
            Default is 'en' for English.

        raise_errors: (optional) If True, errors will be raised if the text cannot be parsed.
            If False, a (`None`, `None`) tuple will be returned in case of errors.

    Returns:
        None | tuple[datetime, datetime | None] | list[tuple[datetime, datetime | None]] : The parsed time-span tuple(s).

    Examples:
        >>> parse('last month')  # if today would be in February 2024
        (datetime.datetime(2024, 1, 1, 0, 0), datetime.datetime(2024, 1, 31, 23, 59, 59, 999999))
    """
    parser = Parser(lang_iso_639_1, raise_errors)
    result = parser.parse(text)
    if isinstance(result, list):
        if len(result) > 1:
            return result
        return result[0]  # unwrap tuple from list
    return result  # return tuple


class Parser:
    """
    Date- and time-related text parser for supported languages.
    As of now, only language `en` is supported.
    """

    def __init__(self, lang_iso_639_1: Literal["en"] = "en", raise_errors: bool = False):
        """
        Initializes a date text parser for the given language.

        Arguments:
            lang_iso_639_1: The ISO 639-1 2-digit language code for the language of the text to parse.
                Default is 'en' for English.
            raise_errors: If True, errors will be raised if the text cannot be parsed.
                If False, a (`None`, `None`) tuple will be returned in case of errors.
        """
        self._raise_errors: bool = raise_errors
        try:
            self._parser: DateTextLanguageParser = self._load_parser(lang_iso_639_1)
        except ImportError as e:
            raise ValueError(f"Parsing date text for language '{lang_iso_639_1}' is not supported. "
                             f"Failed to load and instance module/class '{self._modul_name(lang_iso_639_1)}'") from e

    def _modul_name(self, language: str) -> str:
        """ Returns the expected module name for a given language."""
        return f'cubedpandas.datetext.parser_{language}.DateTextParser'

    @property
    def language(self) -> str:
        """ Returns the ISO 639-1 language 2-difit code of the parser, e.g. 'en' for English."""
        return self._parser.language

    @property
    def raise_errors(self) -> bool:
        """ Returns True if errors will be raised if a text cannot be parsed."""
        return self._raise_errors

    @raise_errors.setter
    def raise_errors(self, value: bool):
        """ Sets if errors will be raised if a text cannot be parsed."""
        self._raise_errors = value

    def parse(self, text: str, parser_info: parserinfo | None = None) \
            -> (tuple[datetime | None, datetime | None] |
                list[tuple[datetime | None, datetime | None]]):
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
        try:
            return self._parser.parse(text, parser_info)
        except ValueError as e:
            if self._raise_errors:
                raise e
            return None, None

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
