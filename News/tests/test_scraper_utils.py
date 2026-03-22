import re
import tempfile
import unittest
from pathlib import Path

try:
    from News.common.scraper_utils import build_end_date, join_text, write_json_records
    IMPORT_ERROR = None
except Exception as error:
    IMPORT_ERROR = error


class FakeElement:
    def __init__(self, text):
        self._text = text

    def get_text(self, strip=False):
        return self._text.strip() if strip else self._text


class ScraperUtilsTests(unittest.TestCase):
    @unittest.skipIf(IMPORT_ERROR is not None, f"missing dependencies: {IMPORT_ERROR}")
    def test_build_end_date_format(self):
        value = build_end_date(days_back=1)
        self.assertRegex(value, r"^\\d{4}-\\d{2}-\\d{2}$")

    @unittest.skipIf(IMPORT_ERROR is not None, f"missing dependencies: {IMPORT_ERROR}")
    def test_join_text(self):
        items = [FakeElement("hello"), FakeElement("world")]
        self.assertEqual(join_text(items), "helloworld")
        self.assertEqual(join_text(items, sep=" "), "hello world")

    @unittest.skipIf(IMPORT_ERROR is not None, f"missing dependencies: {IMPORT_ERROR}")
    def test_write_json_records_creates_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = write_json_records(
                records=[{"title": "demo"}],
                source_name="TEST",
                category="sample",
                base_output_dir=temp_dir,
                file_prefix="test",
            )
            self.assertTrue(Path(file_path).exists())


if __name__ == "__main__":
    unittest.main()
