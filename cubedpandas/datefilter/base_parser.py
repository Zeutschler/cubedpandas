from abc import ABC, abstractmethod
from datetime import datetime
from dateutil.parser import parserinfo
from cubedpandas.datefilter.date_span import DateSpan


class DateTextLanguageParser(ABC):
    """Base class for language specific date filter parsers."""

    @property
    @abstractmethod
    def language(self) -> str:
        pass

    @abstractmethod
    def parse(self, text: str, parser_info: None | parserinfo = None) -> DateSpan | list[DateSpan]:
        pass
