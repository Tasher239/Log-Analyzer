import glob
from src.iterators.base_iterator import BaseIterator
from typing import Iterator


class LocalPathIterator(BaseIterator):
    """
    Реализует итератор для обхода файлов по локальному пути
    """

    def __init__(self, path_pattern: str):
        self._files: list[str] = glob.glob(path_pattern)

    @property
    def files(self) -> list[str]:
        return self._files

    def __iter__(self) -> Iterator[str]:
        for file_path in self.files:
            with open(file_path, "r") as file:
                for line in file:
                    if line.strip():
                        yield line.strip()
