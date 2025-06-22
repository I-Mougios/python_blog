import importlib
from itertools import chain
from pathlib import Path

import pytest

csv_reader_module = importlib.import_module("year.2025.May.csv_reader")
CSVBatchReader = csv_reader_module.CSVBatchReader


class TestCSVBatchReader:
    def setup_method(self, method):
        print(f"Running setup method for {method.__name__}")
        self.csv_file = Path(__file__).parent / "test_data.csv"
        parent_dir = self.csv_file.parent
        self.cleansed_file = parent_dir / (self.csv_file.stem + "_cleaned" + self.csv_file.suffix)
        self.errors = parent_dir / (self.csv_file.stem + "_invalid_rows" + self.csv_file.suffix)

        headers = b"id#!name#!age#!city#!score\n"
        good_lines = (
            b"1#!Alice#!30#!Athens#!85\n"
            b"2#!Bob#!25#!Patras#!90\n"
            b"3#!Charlie#!22#!Thessaloniki#!88\n"
            b"4#!Diana#!28#!Heraklion#!92\n"
            b"5#!Evan#!35#!Volos#!80\n"
        )
        bad_line = b"6#!Zo\xffe#!29#!Ioannina#!75\n"  # invalid UTF-8
        # delimiters to try -- (";", "|", "`", ":", "~", "$")
        line_with_all_delimiters = b"value1;value2|value3`value4:value5~value6~value7$value8\n"

        # Build test-specific content
        if method.__name__ == "test_with_headers_clean_data":
            content = headers + good_lines
        elif method.__name__ == "test_no_headers_clean_data":
            content = good_lines
        elif method.__name__ == "test_with_headers_and_bad_line":
            content = headers + good_lines + bad_line
        elif method.__name__ == "test_no_headers_and_bad_line":
            content = good_lines + bad_line
        elif method.__name__ == "test_raise_delimiter_error":
            content = headers + good_lines + line_with_all_delimiters
        elif method.__name__ == "test_replace_headers_and_bad_line":
            content = headers + good_lines + bad_line
        elif method.__name__ == "test_replace_headers_clean_data":
            content = headers + good_lines

        self.csv_file.write_bytes(content)

    def teardown_method(self, method):
        try:
            self.csv_file.unlink(missing_ok=True)
            self.cleansed_file.unlink(missing_ok=True)
            self.errors.unlink(missing_ok=True)
        except Exception as e:
            print(f"Failed to remove all files:\n {e}")

    def test_with_headers_clean_data(self):
        batch_size = 3
        reader = CSVBatchReader(self.csv_file, batch_size=batch_size, delimiter="#!")
        flattened_reader = enumerate(chain.from_iterable(reader), start=1)

        for i, row in flattened_reader:
            if i == 1:
                assert row["name"] == "Alice" and row["score"] == "85"
            if i == 5:
                assert row["name"] == "Evan" and row["score"] == "80"

        assert not self.cleansed_file.exists()
        assert not self.errors.exists()

    def test_no_headers_clean_data(self):
        batch_size = 2
        custom_headers = ["id", "name", "age", "city", "score"]
        reader = CSVBatchReader(
            self.csv_file,
            batch_size=batch_size,
            delimiter="#!",
            headers=custom_headers,
            drop_headers=False,
        )

        batch = next(reader)
        rows = list(batch)

        assert len(rows) == batch_size
        assert rows[0]["id"] == "1"
        assert rows[1]["name"] == "Bob"

    def test_with_headers_and_bad_line(self):
        batch_size = 2
        reader = CSVBatchReader(self.csv_file, batch_size=batch_size, delimiter="#!")

        # Trigger reading the file, which should raise and auto-clean internally
        batch = next(reader)
        rows = list(batch)
        assert len(rows) == batch_size
        assert rows[0]["name"] == "Alice"
        assert rows[0]["age"] == "30"

        assert self.cleansed_file.exists()
        assert self.errors.exists()

        cleaned_text = self.cleansed_file.read_text(encoding="utf-8")
        assert "Zo" not in cleaned_text  # The bad line should not be in the cleaned version
        assert "1#!Alice#!30#!Athens#!85\n" in cleaned_text  # The other lines should be in the clean text

        with self.errors.open("rb") as f:
            error_lines = f.readlines()
            assert (
                b"[Line 7] 6#!Zo\xffe#!29#!Ioannina#!75\n" in error_lines[0]
            )  # Our invalid line is reported correctly

    def test_no_headers_and_bad_line(self):
        batch_size = 2
        custom_headers = ["Col1", "Col2", "Col3", "Col4", "Col5"]
        reader = CSVBatchReader(
            self.csv_file,
            batch_size=batch_size,
            delimiter="#!",
            headers=custom_headers,
            drop_headers=False,
        )

        batch = next(reader)
        rows = list(batch)
        first_row = rows[0]
        assert first_row["Col1"] == "1"
        assert first_row["Col2"] == "Alice"
        assert first_row["Col3"] == "30"

    def test_raise_delimiter_error(self):
        with pytest.raises(csv_reader_module.DelimiterError):
            with CSVBatchReader(self.csv_file, batch_size=None, delimiter="#!") as batches:
                for batch in batches:
                    list(batch)

    def test_replace_headers_and_bad_line(self):
        batch_size = 2
        custom_headers = ["Col1", "Col2", "Col3", "Col4", "Col5"]
        reader = CSVBatchReader(
            self.csv_file,
            batch_size=batch_size,
            delimiter="#!",
            headers=custom_headers,
            drop_headers=True,
        )

        batch = next(reader)
        rows = list(batch)
        first_row = rows[0]
        assert first_row["Col1"] == "1"
        assert first_row["Col2"] == "Alice"
        assert first_row["Col3"] == "30"

        assert self.cleansed_file.exists()
        assert self.errors.exists()

        cleaned_text = self.cleansed_file.read_text(encoding="utf-8")
        assert "Zo" not in cleaned_text
        assert "1#!Alice#!30#!Athens#!85\n" in cleaned_text

        with self.errors.open("rb") as f:
            error_lines = f.readlines()
            assert b"[Line 7] 6#!Zo\xffe#!29#!Ioannina#!75\n" in error_lines[0]

    def test_replace_headers_clean_data(self):
        batch_size = 2
        custom_headers = ["Col1", "Col2", "Col3", "Col4", "Col5"]
        reader = CSVBatchReader(
            self.csv_file,
            batch_size=batch_size,
            delimiter="#!",
            headers=custom_headers,
            drop_headers=True,
        )

        batch = next(reader)
        rows = list(batch)
        first_row = rows[0]
        assert first_row["Col1"] == "1"
        assert first_row["Col2"] == "Alice"
        assert first_row["Col3"] == "30"

        assert not self.cleansed_file.exists()
        assert not self.errors.exists()
