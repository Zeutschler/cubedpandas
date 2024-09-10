from abc import ABC, abstractmethod
from datetime import datetime
from dateutil.parser import parserinfo


class DateTextLanguageParser(ABC):
    """Base class for language specific datetext parsers."""

    @property
    @abstractmethod
    def language(self) -> str:
        pass

    @abstractmethod
    def parse(self, text: str, parser_info: None | parserinfo = None) -> (tuple[datetime | None, datetime | None] |
                                                                          list[
                                                                              tuple[datetime | None, datetime | None]]):
        pass
