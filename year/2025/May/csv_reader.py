import csv
from itertools import islice
from pathlib import Path
from typing import Iterable, Optional, Union

from icecream import ic


def clean_file(input_path: Path, encoding: str = "utf-8") -> Path:
    """Creates a cleaned version of the file with problematic lines removed"""
    input_dir = input_path.parent  # directory containing input file

    output_name = input_path.stem + "_cleaned" + input_path.suffix
    error_name = input_path.stem + "_invalid_rows" + input_path.suffix

    output_path = input_dir / output_name
    error_path = input_dir / error_name

    with (
        open(input_path, "rb") as infile,
        open(output_path, "w", encoding="utf-8") as cleansed_file,
        open(error_path, "wb") as errorfile,
    ):

        for i, raw_line in enumerate(infile, start=1):
            try:
                line = raw_line.decode(encoding)
                cleansed_file.write(line)
            except UnicodeDecodeError:
                prefix = f"[Line {i}] ".encode("utf-8")
                errorfile.write(prefix + raw_line)

    return output_path


class DelimiterError(Exception):
    """Raised none of specified delimiters is available"""

    pass


class CSVBatchReader:
    def __init__(
        self,
        filepath: Union[str, Path],
        batch_size: int = 10000,
        delimiter: str = ",",
        encoding: str = "utf-8",
        headers: Optional[Iterable[str]] = None,
        drop_headers: bool = False,
        nrows: Optional[int] = None,
        dictreader_kwargs: Optional[dict] = None,
        **open_kwargs,
    ):

        self.filepath = Path(filepath)
        self.batch_size = batch_size
        self.delimiter = delimiter
        self.encoding = encoding
        self._headers = headers
        self.drop_headers = drop_headers
        self.nrows = nrows
        self.dictreader_kwargs = dictreader_kwargs or {}
        self.open_kwargs = open_kwargs
        self._file = None

    @property
    def file(self):
        if self._file is None:
            self._file = open(self.filepath, "r", encoding=self.encoding, **self.open_kwargs)
            self.resolve_headers()
        return self._file

    def __enter__(self):
        """Support Context Manager Protocol"""
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        """Ensure file is closed when exiting context"""
        if self._file and not self._file.closed:
            self.file.close()
        return False  # do not suppress exceptions

    def __iter__(self):
        return self

    def __next__(self):
        batch = self._get_batch()
        if not batch:
            self.file.close()
            raise StopIteration

        if len(self.delimiter) > 1:
            delimiter, batch = self.replace_delimiter(batch)
        else:
            delimiter = self.delimiter

        dict_reader = csv.DictReader(batch, delimiter=delimiter, fieldnames=self._headers, **self.dictreader_kwargs)
        if self.nrows:
            dict_reader = islice(dict_reader, self.nrows)

        return dict_reader

    def resolve_headers(self):
        """
        Determine the headers based on the initialization parameters
            Case 1: Headers explicitly provided and file has its own headers
            Case 2: Need to read the headers from the file
            Case 3: Headers explicitly provided and file starts with actual data
        """
        # Case 1: Headers were explicitly provided
        if self._headers is not None:
            # Skip first line if headers are provided and file has its own headers
            if self.drop_headers:
                self._get_first_line()
            # Case 3: File starts with actual data
            return
        # Case 2: Need to read headers from file.
        # drop_header parameter has no effect if headers is None
        first_line = self._get_first_line()
        self._headers = first_line.strip("\r\n").split(self.delimiter)

    def _get_first_line(self):
        """Get the first line from the file but handle the case of a UnicodeDecodeError"""
        try:
            return next(self.file)
        except UnicodeDecodeError as ex:
            ic(ex)
            self._handle_unicode_error()
            return next(self.file)

    def _get_batch(self):
        try:
            batch = list(islice(self.file, self.batch_size))
        except UnicodeDecodeError as ex:
            ic(ex)
            self._handle_unicode_error()
            batch = list(islice(self.file, self.batch_size))
        return batch

    def _handle_unicode_error(self):
        """
        Description:
            - Read the file in binary mode
            - Decode based on the self.encoding
            - Write the valid line in utf-8
            - Write separately invalid lines in binary mode
            - Change the filename to point to the new filename(clean file)
            - Change the encoding of the file to utf-8
            - Reset the file property to force re-open the new file
        """
        output_file = clean_file(self.filepath, self.encoding)
        self.filepath = output_file
        self.encoding = "utf-8"

        if self._file:
            try:
                self._file.close()
            except Exception:  # noqa: S110
                pass

        self._file = open(self.filepath, "r", encoding=self.encoding, **self.open_kwargs)

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
        delimiters = (";", "|", "`", ":", "~", "$")
        for delimiter in delimiters:
            if not any(delimiter in line for line in lines):
                return delimiter, (line.replace(self.delimiter, delimiter) for line in lines)

        raise DelimiterError(f"All specified delimiters {delimiters} found in the data")
