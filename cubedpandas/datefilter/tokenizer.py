from enum import IntEnum
from typing import Any
import re
from datetime import datetime, time
from dateutil.parser import parse as dateutil_parse, ParserError, parserinfo


class TokenType(IntEnum):
    # Token types for date text parsing
    WHITESPACE = 0

    DATE = 1  # a date parseable by dateutil.parser.parse
    TIME = 2  # a date parseable by dateutil.parser.parse
    TIME_POSTFIX = 3  # e.g. 'am', 'pm' >>> "10:00 am", "12:00 pm"
    DATE_TIME = 4  # a date parseable by dateutil.parser.parse
    DATE_TIME_RANGE = 5  # a from-to date range

    WEEKDAY = 6  # e.g. 'monday', 'tuesday', 'wednesday' >>> "Monday"
    WEEK = 7  # e.g. '1', '2', '3' >>> "Week 1"
    MONTH = 8  # e.g. 'january', 'february', 'march' >>> "January 2024"
    YEAR = 9  # e.g. '2024', '2025', '2026' >>> "January 2024"

    MSECOND_POSTFIX = 10  # e.g. 'ms', 'millisecond', 'milliseconds' >>> "5 milliseconds"
    SECOND_POSTFIX = 11  # e.g. 's', 'sec', 'secs', 'second', 'seconds' >>> "5 seconds"
    MINUTE_POSTFIX = 12  # e.g. 'm', 'min', 'mins', 'minute', 'minutes' >>> "5 minutes"
    HOUR_POSTFIX = 13  # e.g. 'h', 'hr', 'hrs', 'hour', 'hours' >>> "5 hours"
    DAY_POSTFIX = 14  # e.g. 'd', 'day', 'days' >>> "5 days"
    WEEK_POSTFIX = 15  # e.g. 'w', 'wk', 'wks', 'week', 'weeks' >>> "5 weeks"
    MONTH_POSTFIX = 16  # e.g. 'mo', 'month', 'months' >>> "5 months"
    YEAR_POSTFIX = 17  # e.g. 'y', 'yr', 'yrs', 'year', 'years' >>> "5 years"
    QUARTER_POSTFIX = 18  # e.g. 'q', 'qtr', 'qtrs', 'quarter', 'quarters' >>> "5 quarters"

    LIST_DELIMITER = 20  # e.g. ',' >>> "Monday, Tuesday, Wednesday"
    RANGE_INFIX = 21  # e.g. '-', 'to', 'and' >>> "10:00 to 12:00", "between 10:00 and 12:00"
    RANGE_PREFIX = 22  # e.g. 'between', 'from' >>> "from 10:00 to 12:00", "between 10:00 and 12:00"
    OFFSET = 23  # e.g. 'next', 'last', 'previous', 'this' >>> "next week", "last month"
    #      but also 'in', 'ago' >>> "in 5 days", "5 days ago"
    DATE_INFIX = 24  # e.g. 'of' >>> "1st of January 2024"

    NUMBER = 80
    NUMBER_POSTFIX = 81  # e.g. 'st', 'nd', 'rd', 'th' >>> "5th" or '1.' >>> "1st"

    WORD = 90
    TUPLE = 91
    UNKNOWN = 99

    def __str__(self):
        return self.name


ALIASES = {
    # weekdays
    'tue': 'tuesday',
    'wed': 'wednesday',
    'thu': 'thursday',
    'fri': 'friday',
    'sat': 'saturday',
    'sun': 'sunday',

    'mon.': 'monday',
    'tue.': 'tuesday',
    'wed.': 'wednesday',
    'thu.': 'thursday',
    'fri.': 'friday',
    'sat.': 'saturday',
    'sun.': 'sunday',

    'mo': 'monday',
    'tu': 'tuesday',
    'we': 'wednesday',
    'th': 'thursday',
    'fr': 'friday',
    'sa': 'saturday',
    'su': 'sunday',

    'mo.': 'monday',
    'tu.': 'tuesday',
    'we.': 'wednesday',
    'th.': 'thursday',
    'fr.': 'friday',
    'sa.': 'saturday',
    'su.': 'sunday',

    # months
    'jan': 'january',
    'feb': 'february',
    'mar': 'march',
    'apr': 'april',
    'may': 'may',
    'jun': 'june',
    'jul': 'july',
    'aug': 'august',
    'sep': 'september',
    'sept': 'september',
    'oct': 'october',
    'nov': 'november',
    'dec': 'december',

    'jan.': 'january',
    'feb.': 'february',
    'mar.': 'march',
    'apr.': 'april',
    'jun.': 'june',
    'jul.': 'july',
    'aug.': 'august',
    'sep.': 'september',
    'sept.': 'september',
    'oct.': 'october',
    'nov.': 'november',
    'dec.': 'december',

    # postfixes
    's': 'second',
    'sec': 'second',
    'secs': 'second',
    'second': 'second',
    'seconds': 'second',

    'm': 'minute',
    'min': 'minute',
    'mins': 'minute',
    'minute': 'minute',
    'minutes': 'minute',

    'h': 'hour',
    'hr': 'hour',
    'hrs': 'hour',
    'hour': 'hour',
    'hours': 'hour',

    'd': 'day',
    'day': 'day',
    'days': 'day',

    'mon': 'month',
    'month': 'month',
    'months': 'month',

    'y': 'year',
    'yr': 'year',
    'yrs': 'year',
    'year': 'year',
    'years': 'year',

    'q': 'quarter',
    'qtr': 'quarter',
    'qtrs': 'quarter',
    'quarter': 'quarter',
    'quarters': 'quarter',

    'w': 'week',
    'wk': 'week',
    'wks': 'week',
    'week': 'week',
    'weeks': 'week',

    # others
    # time related
    'a.m.': 'am',
    'p.m.': 'pm',
}

KEYWORDS = {
    # weekdays
    "monday": ['monday', 1, TokenType.WEEKDAY],
    "tuesday": ['tuesday', 2, TokenType.WEEKDAY],
    "wednesday": ['wednesday', 3, TokenType.WEEKDAY],
    "thursday": ['thursday', 4, TokenType.WEEKDAY],
    "friday": ['friday', 5, TokenType.WEEKDAY],
    "saturday": ['saturday', 6, TokenType.WEEKDAY],
    "sunday": ['sunday', 7, TokenType.WEEKDAY],

    "january": ['january', 1, TokenType.MONTH],
    "february": ['february', 2, TokenType.MONTH],
    "march": ['march', 3, TokenType.MONTH],
    "april": ['april', 4, TokenType.MONTH],
    "may": ['may', 5, TokenType.MONTH],
    "june": ['june', 6, TokenType.MONTH],
    "july": ['july', 7, TokenType.MONTH],
    "august": ['august', 8, TokenType.MONTH],
    "september": ['september', 9, TokenType.MONTH],
    "october": ['october', 10, TokenType.MONTH],
    "november": ['november', 11, TokenType.MONTH],
    "december": ['december', 12, TokenType.MONTH],

    # postfixes
    "second": ['second', None, TokenType.SECOND_POSTFIX],
    "minute": ['minute', None, TokenType.MINUTE_POSTFIX],
    "hour": ['hour', None, TokenType.HOUR_POSTFIX],
    "day": ['day', None, TokenType.DAY_POSTFIX],
    "month": ['month', None, TokenType.MONTH_POSTFIX],
    "year": ['year', None, TokenType.YEAR_POSTFIX],
    "quarter": ['quarter', None, TokenType.QUARTER_POSTFIX],
    "week": ['week', None, TokenType.WEEK_POSTFIX],

    "am": ['am', 0, TokenType.TIME_POSTFIX],
    "pm": ['pm', 12, TokenType.TIME_POSTFIX],

    # others
    "over": ['next', 1, TokenType.OFFSET],
    "next": ['next', 1, TokenType.OFFSET],
    "last": ['last', -1, TokenType.OFFSET],
    "previous": ['previous', -1, TokenType.OFFSET],
    "this": ['this', 0, TokenType.OFFSET],
    "in": ['in', 1, TokenType.OFFSET],
    "ago": ['ago', 1, TokenType.OFFSET],
    "of": ['of', None, TokenType.DATE_INFIX],

    ",": [',', None, TokenType.LIST_DELIMITER],
    ";": [',', None, TokenType.LIST_DELIMITER],
    "-": ['-', None, TokenType.RANGE_INFIX],
    "to": ['to', None, TokenType.RANGE_INFIX],
    "and": ['and', None, TokenType.RANGE_INFIX],
    "between": ['between', None, TokenType.RANGE_PREFIX],

    "now": ['now', None, TokenType.DATE_TIME_RANGE],
    "tomorrow": ['tomorrow', None, TokenType.DATE_TIME_RANGE],
    "today": ['today', None, TokenType.DATE_TIME_RANGE],
    "yesterday": ['yesterday', None, TokenType.DATE_TIME_RANGE],

}

ORDINAL_POSTFIXES = ['st', 'nd', 'rd', 'th']

POSTFIXES = [TokenType.SECOND_POSTFIX, TokenType.MINUTE_POSTFIX, TokenType.HOUR_POSTFIX,
             TokenType.DAY_POSTFIX, TokenType.MONTH_POSTFIX, TokenType.YEAR_POSTFIX,
             TokenType.QUARTER_POSTFIX, TokenType.WEEK_POSTFIX]

CALENDER_KEYWORDS = [TokenType.WEEKDAY, TokenType.MONTH, TokenType.YEAR]

DATETIME_REFERENCE = [TokenType.DATE, TokenType.TIME, TokenType.DATE_TIME,
                      TokenType.WEEKDAY, TokenType.WEEK, TokenType.MONTH, TokenType.YEAR]

RE_TIME_FORMAT = re.compile(r"^([0-9]|[0-1][0-9]|2[0-3]):[0-5][0-9]?(:[0-5][0-9])?(?:[.,][0-9]+)?$")


class DateTimeTuple:
    def __init__(self, year=None, month=None, day=None,
                 hour=None, minute=None, second=None,
                 millisecond=None, microsecond=None):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.millisecond = millisecond
        self.microsecond = microsecond

    @property
    def has_year(self) -> bool:
        return self.year is not None

    @property
    def has_month(self) -> bool:
        return self.month is not None

    @property
    def has_day(self) -> bool:
        return self.day is not None

    @property
    def has_hour(self) -> bool:
        return self.hour is not None

    @property
    def has_minute(self) -> bool:
        return self.minute is not None

    @property
    def has_second(self) -> bool:
        return self.second is not None

    @property
    def has_millisecond(self) -> bool:
        return self.millisecond is not None

    @property
    def has_microsecond(self) -> bool:
        return self.microsecond is not None

    def to_datetime(self, ref_datetime: datetime = None):
        if ref_datetime is None:
            ref_datetime = datetime.now()
        year = self.year if self.has_year else ref_datetime.year
        month = self.month if self.has_month else ref_datetime.month
        day = self.day if self.has_day else ref_datetime.day
        hour = self.hour if self.has_hour else ref_datetime.hour
        minute = self.minute if self.has_minute else ref_datetime.minute
        second = self.second if self.has_second else ref_datetime.second
        microsecond = self.millisecond * 1000 if self.has_millisecond else ref_datetime.microsecond
        if self.has_microsecond:
            microsecond = self.microsecond if self.has_microsecond else ref_datetime.microsecond % 1000
        return datetime(year, month, day, hour, minute, second, microsecond)

    def __add__(self, other):
        if isinstance(other, DateTimeTuple):
            return DateTimeTuple(year=other.year if self.has_year else self.year,
                                 month=other.month if self.has_month else self.month,
                                 day=other.day if self.has_day else self.day,
                                 hour=other.hour if self.has_hour else self.hour,
                                 minute=other.minute if self.has_minute else self.minute,
                                 second=other.second if self.has_second else self.second,
                                 millisecond=other.millisecond if self.has_millisecond else self.millisecond,
                                 microsecond=other.microsecond if self.has_microsecond else self.microsecond
                                 )
        raise ValueError(f"Unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'")

    def __str__(self):
        args = []
        if self.has_year:
            args.append(f"year={self.year}")
        if self.has_month:
            args.append(f"month={self.month}")
        if self.has_day:
            args.append(f"day={self.day}")
        if self.has_hour:
            args.append(f"hour={self.hour}")
        if self.has_minute:
            args.append(f"minute={self.minute}")
        if self.has_second:
            args.append(f"second={self.second}")
        if self.has_millisecond:
            args.append(f"millisecond={self.millisecond}")
        if self.has_microsecond:
            args.append(f"microsecond={self.microsecond}")
        return f"DateTimeTuple({', '.join(args)})"

    def __repr__(self):
        return self.__str__()


class Token:
    """Represents a token in a date text."""

    def __init__(self, token_text: str, token_type=TokenType.UNKNOWN, value=None, raw_text=None):
        self.type: TokenType = token_type
        self.text: str = token_text
        self.raw_text: str = raw_text if raw_text else token_text
        self.ordinal: int = 0
        self.value: Any = value
        self.priority: int = 0

    def __str__(self):
        return f"{'.' * (16 - len(self.type.name))}{self.type}: '{self.text}' , value:={self.value}"

    def __repr__(self):
        return self.__str__()


class TokenList(list):
    """A navigable list of tokens."""

    def __init__(self, tokens: list[Token]):
        super().__init__(tokens)
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self):
            self.index += 1
            return self[self.index - 1]
        else:
            raise StopIteration

    def peek(self):
        if self.index < len(self):
            return self[self.index]
        else:
            return None

    def next(self):
        if self.index < len(self):
            self.index += 1
            return self[self.index - 1]
        else:
            return None

    def previous(self):
        if self.index > 0:
            self.index -= 1
            return self[self.index]
        else:
            return None

    def offset(self, offset: int):
        if -1 < self.index + offset < len(self):
            return self[self.index + offset]
        else:
            return None

    def remaining(self):
        return self[self.index:]

    def has_next(self):
        return self.index < len(self)

    def has_previous(self):
        return self.index > 0

    def reset(self):
        self.index = 0

    def __str__(self):
        return f"TokenList({super().__str__()})"

    def __repr__(self):
        return f"TokenList({super().__repr__()})"


class Tokenizer:
    """Tokenizes a date text into a list of tokens."""

    @staticmethod
    def tokenize(text: str, parser_info: parserinfo | None = None) -> TokenList:

        # 1st run - raw token processing
        stack = []
        text_tokens = Tokenizer.split_tokens(text)
        tokens: list[Token] = []
        for text in text_tokens:
            if text == "":
                continue
            while len(stack) > 0:
                tokens.append(stack.pop())

            # extract delimiters
            if text.endswith(","):
                stack.append(Token(",", TokenType.LIST_DELIMITER))
                text = text[:-1]

            # translate aliases and process date text keywords
            raw_text = text
            text = ALIASES.get(text, text)
            if text in KEYWORDS:
                text, value, token_type = KEYWORDS[text]
                tokens.append(Token(text, token_type, value, raw_text))
                continue

            if text.isdigit():
                number = int(text)
                if 1900 <= number <= 2100:
                    tokens.append(Token(text, TokenType.YEAR, number))
                else:
                    tokens.append(Token(text, TokenType.NUMBER, number))
                continue

            if text[0].isdigit():
                # check for ordinal dates like '1.' in '1. of January'
                if len(text) > 1:
                    postfix = text[-1:]
                    if postfix == ".":
                        number_text = text[:-1]
                        if number_text.isdigit():
                            tokens.append(Token(number_text, TokenType.NUMBER, int(number_text)))
                            tokens.append(Token(postfix, TokenType.NUMBER_POSTFIX))
                            continue
                # check for ordinal date or week numbers like '1st', '2nd', '3rd', '4th', ...
                if len(text) > 2:
                    postfix = text[-2:]
                    if postfix in ORDINAL_POSTFIXES:
                        number_text = text[:-2]
                        if number_text.isdigit():
                            tokens.append(Token(number_text, TokenType.NUMBER, int(number_text)))
                            tokens.append(Token(postfix, TokenType.NUMBER_POSTFIX))
                            continue

            # check for valid time and date tokens
            if RE_TIME_FORMAT.match(text):
                tokens.append(Token(text, TokenType.TIME, dateutil_parse(text, parser_info, fuzzy=True).time()))
                continue
            try:
                date = dateutil_parse(text, parser_info, fuzzy=True)
                if date.time() == time(0, 0, 0):
                    tokens.append(Token(text, TokenType.DATE, date))
                else:
                    tokens.append(Token(text, TokenType.DATE_TIME, date))
                continue

            except (ParserError, OverflowError):
                pass

            token = Token(text, TokenType.UNKNOWN)
            tokens.append(token)

        # push remaining stack to tokens
        if len(stack) > 0:
            tokens.extend(stack)

        # Post-processing...
        # ...if just 1 token text
        if len(tokens) == 1:
            token = tokens[0]
            if token.type in CALENDER_KEYWORDS:  # month or weekday names or year number
                token.type = TokenType.DATE_TIME_RANGE

        return TokenList(tokens)

    @staticmethod
    def split_tokens(text) -> list[str]:
        if "\n" in text:
            text = "".join(text.splitlines())  # multi-line text to single line
        text = text.lower().strip()
        if "_" in text and " " not in text:  # replace underscores with spaces, e.g. 'cdf.last_month'
            text = text.replace("_", " ")
        if " " in text:
            tokens = text.split()
            tokens = [t for t in tokens if t != ""]
        else:
            tokens = [text, ]
        return tokens
