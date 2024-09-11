from unittest import TestCase
from datetime import date, datetime
from dateutil.parser import parse
from cubedpandas.datetext import parse
from cubedpandas.datetext.tokenizer import Tokenizer, Token, TokenType

class TestDateTextParser(TestCase):
    def setUp(self):
        self.debug = self.is_debug()

    @staticmethod
    def is_debug():
        import sys
        gettrace = getattr(sys, 'gettrace', None)
        if gettrace is None:
            return False
        else:
            v = gettrace()
            if v is None:
                return False
            else:
                return True

    def test_initial_parse_using_dateutil(self):
        text = "2024-09-09"
        result = parse(text)
        self.assertEqual(result[0], datetime(2024, 9, 9))

    def test_single_word(self):
        text = "today"
        result = parse(text)
        self.assertEqual(result[0], datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))
        self.assertEqual(result[1], datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999))

    def test_single_word_month(self):
        words = ["today", "yesterday", "tomorrow", "week", "month", "quarter", "year", "ytd", "mtd", "qtd", "wtd",
                 "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
                 "january", "february", "march", "april", "may", "june",
                 "july", "august", "september", "october", "november", "december",
                 ]
        for word in words:
            result = parse(word)
            if self.debug:
                print(f"{word} = {result[0]} - {result[1]}")

    def test_tokenizer(self):
        datetexts = ["1st of January 2024",
                     "1st day of January, February and March 2024",
                     "last week",
                     "next 3 days",
                     "3rd week of 2024",
                     "08.09.2024", "2024/09/08", "2024-09-08",
                     "19:00", "1:34:45", "1:34:45.123", "1:34:45.123456",
                     "2007-08-31T16:47+00:00", "2007-12-24T18:21Z", "2008-02-01T09:00:22+05",
                     "2009-01-01T12:00:00+01:00", "2010-01-01T12:00:00.001+02:00"]

        for text in datetexts:
            tokens = Tokenizer.tokenize(text)
            if self.debug:
                print(f"\nTokens for '{text}':")
                for pos, token in enumerate(tokens):
                    print(f"{pos + 1:03d}: {token}")
