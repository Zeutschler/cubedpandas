from abc import abstractproperty, abstractmethod, ABC
from typing import Literal, LiteralString, TypeAlias
from datetime import datetime

from dateutil.parser import parse as dateutil_parse, parserinfo
from dateutil.parser import ParserError
from dateutil.relativedelta import relativedelta

from cubedpandas.datetext.base_parser import DateTextLanguageParser
from cubedpandas.datetext.tokenizer import Tokenizer, Token, TokenType
import cubedpandas.datetext.methods as dtm

resolvers = {"now": dtm.now, "tomorrow": dtm.tomorrow, "today": dtm.today, "yesterday": dtm.yesterday,
             "ytd": dtm.ytd, "mtd": dtm.mtd, "qtd": dtm.qtd, "wtd": dtm.wtd,
             "month": dtm.month, "week": dtm.week, "quarter": dtm.quarter, "year": dtm.year,
             "monday": dtm.monday, "tuesday": dtm.tuesday, "wednesday": dtm.wednesday, "thursday": dtm.thursday,
             "friday": dtm.friday, "saturday": dtm.saturday, "sunday": dtm.sunday,
             "january": dtm.january, "february": dtm.february, "march": dtm.march, "april": dtm.april,
             "may": dtm.may, "june": dtm.june, "july": dtm.july, "august": dtm.august,
             "september": dtm.september, "october": dtm.october, "november": dtm.november,
             "december": dtm.december,
             }


class DateTextParser(DateTextLanguageParser):
    """
    English language DateText parser. Converts date- and time-related text
    in English language into a (`datetime`, `datetime`) time-span tuples.
    """
    LANGUAGE: str = "en"

    def __init__(self):
        self.tokenizer = Tokenizer()
        self.tokens: list[Token] = []

    @property
    def language(self) -> str:
        return self.LANGUAGE

    def parse(self, text: str, parser_info: parserinfo | None = None) \
            -> (tuple[datetime | None, datetime | None] |
                list[tuple[datetime | None, datetime | None]]):

        # First, we try to parse the text with dateutil.
        tokens = self.tokenizer.tokenize(text, parser_info)
        if len(tokens) == 0:
            raise ValueError("Failed to parse empty date text string.")
        result = self.parse_tokens(tokens, parser_info)
        if result != (None, None):
            return result

        # Finally, the dateutil library is used to (try to) parse the text.
        # For details please visit: https://dateutil.readthedocs.io/en/stable/index.html
        # Note: Dateutil does not return tuples for single dates, and has different
        #       behavior for some date texts. e.g. if its Tuesday, then `Monday` refers
        #       to the next Monday, but want it to be the monday of this week.
        try:
            result = dateutil_parse(text, fuzzy=True)
            return result, None
        except (ParserError, OverflowError) as e:
            return None, None

    def parse_tokens(self, tokens: list[Token], parser_info: parserinfo | None = None):
        """ Parses a list of tokens into a (`datetime`, `datetime`) time-span tuple."""

        # Special case: 1-word date text, e.g. "today", "yesterday" etc.
        if len(tokens) == 1:
            if tokens[0].text in resolvers:
                return resolvers[tokens[0].text]()

        # Failed to parse the text
        return None, None



# endregion
