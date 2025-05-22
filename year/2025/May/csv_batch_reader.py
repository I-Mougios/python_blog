import csv
from itertools import islice
from typing import Union, Optional, Iterable
from pathlib import Path
from icecream import ic


def clean_file(input_path: Path, encoding: str = "utf-8") -> Path:
    """Creates a cleaned version of the file with problematic lines removed"""
    output_name = input_path.stem + "_cleaned" + input_path.suffix
    error_name = "lines_with_bad_encoding.csv"

    with (open(input_path, "rb") as infile,
          open(output_name, "w", encoding=encoding) as cleansed_file,
          open(error_name, "wb") as errorfile):

        for i, raw_line in enumerate(infile, start=1):
            try:
                line = raw_line.decode(encoding)
                cleansed_file.write(line)
            except UnicodeDecodeError:
                prefix = f"[Line {i}] ".encode("utf-8")
                errorfile.write(prefix + raw_line)

    return Path(output_name)

class DelimiterError(Exception):
    """Raised none of specified delimiters is available"""
    pass


class CSVBatchReader:
    def __init__(self,
                 filepath: Union[str, Path],
                 batch_size: int = 10000,
                 delimiter: str = ",",
                 encoding: str = "utf-8",
                 headers: Optional[Iterable[str]] = None,
                 drop_headers: bool = False,
                 ):

        self.filepath = Path(filepath)
        self.batch_size = batch_size
        self.delimiter = delimiter
        self.encoding = encoding
        self._headers = headers
        self.drop_headers = drop_headers
        self._file = None
        self._file_need_cleansing = False

    @property
    def file(self):
        if self._file is None:
            self._file = open(self.filepath, "r", encoding=self.encoding)

        return self._file

    def __enter__(self):
        """Support Context Manager Protocol"""
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        """Ensure file is closed when exiting context"""
        if self.file:
            self.file.close()

        return False  # do not suppress exceptions

    def __iter__(self):
        self.resolve_headers()
        return self

    def __next__(self):
        batch = list(islice(self.file, self.batch_size))
        if not batch:
            self.file.close()
            raise StopIteration

        if len(self.delimiter) > 1:
            delimiter, batch = self.replace_delimiter(batch)
        else:
            delimiter = self.delimiter

        return csv.DictReader(batch, delimiter=delimiter, fieldnames=self._headers)

    def resolve_headers(self):
        """
        Determine the headers based on the initialization parameters
            Case 1: Headers explicitly provided and file has its own headers
            Case 2: Need to read the headers from the file
            Case 3: Headers explicitly provided and file starts with actual data
        """
        print("resolving headers was called")
        # Case 1: Headers were explicitly provided
        if self._headers is not None:
            ic()
            # Skip first line if headers are provided and file has its own headers
            if self.drop_headers:
                ic()
                self._get_first_line()
            # Case 3: File starts with actual data
            return

        ic()
        # Case 2: Need to read headers from file
        first_line = self._get_first_line()
        self._headers = first_line.strip("\r\n").split(self.delimiter)



    def _get_first_line(self):
        """Get the first line from the file but handle the case of a UnicodeDecodeError"""
        try:
            first_line = next(self.file)
        except UnicodeDecodeError:
            output_file = clean_file(self.filepath)
            self.filepath = output_file.name
            self._file = None
            return next(self.file)

    def replace_delimiter(self, lines: Iterable[str]) -> tuple[str, Iterable[str]]:
            """
            Replaces the current delimiter with an unused alternative.

            Args:
                lines: The lines to process

            Returns:
                tuple of (new delimiter, lines with replaced delimiters)

            Raises:
                DelimiterError if no safe replacement can be found
            """
            delimiters = (";", "~", "$")
            for delimiter in delimiters:
                if not any(delimiter in line for line in lines):
                    return delimiter, (line.replace(self.delimiter, delimiter) for line in lines)

            raise DelimiterError(f"All specified delimiters {delimiters} found in the data")


if __name__ == "__main__":
    with open("./data/sample.csv", "wb") as f:
        # f.write(b"id#!name#!signup_date#!score#!active\n")
        f.write(b"1#!Alice#!2023-01-15#!85.5#!True\n")
        f.write(b"2#!Bob#!2023-03-22#!92.0#!False\n")
        f.write(b"3#!Charlie#!2023-05-10#!78.0#!True\n")
        # Inject a truly invalid UTF-8 byte: 0x96
        f.write(b"6#!InvalidChar\x96#!2024-01-01#!75.0#!True\n")
        # -----------------------------------------------------------
        f.write(b"4#!David#!2023-07-30#!88.5#!False\n")
        f.write(b"5#!Eva#!2023-10-01#!95.0#!True\n")
        # Inject a truly invalid UTF-8 byte: 0x96
        f.write(b"7#!SecondInvalidChar\x96#!2024-01-01#!100.0#!True\n")

    batches = CSVBatchReader(filepath="./data/sample.csv",
                        batch_size=4,
                        delimiter="#!",
                        encoding="utf-8",
                        drop_headers=False,
                        headers=['col1', 'col2', 'col3', 'col4', 'col5']
                             )
    print(batches._headers)

    with batches as f:
        for i, batch in enumerate(f, start=1):
            print(f"Batch: {i}")
            for line in batch:
                print(line)



