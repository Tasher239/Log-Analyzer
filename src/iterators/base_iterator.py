from abc import ABC, abstractmethod


class BaseIterator(ABC):
    @property
    @abstractmethod
    def files(self):
        """Должен возвращать список файлов или URL"""
        pass

    @abstractmethod
    def __iter__(self):
        """Должен возвращать итератор для обхода строк в файлах"""
        pass
