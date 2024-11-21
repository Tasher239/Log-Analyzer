import requests
from src.iterators.base_iterator import BaseIterator
from typing import Iterator


class URLPathIterator(BaseIterator):
    """
    Реализует итератор для обхода файлов по url
    """

    def __init__(self, url: str):
        self._files: list[str] = [url]

    @property
    def files(self) -> list[str]:
        return self._files

    def __iter__(self) -> Iterator[str]:
        response = requests.get(self.files[0], stream=True)
        response.raise_for_status()
        for line in response.iter_lines(decode_unicode=True):
            if line.strip():
                yield line.strip()
