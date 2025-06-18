from sample_ext_lib._core import hello_from_bin, read_file, Book

__all__ = ["hello", "read_file", "Book"]


def hello() -> str:
    return hello_from_bin()
