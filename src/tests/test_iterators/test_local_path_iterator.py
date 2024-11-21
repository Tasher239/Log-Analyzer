from src.iterators.local_path_iterator import LocalPathIterator
import tempfile
import os

import unittest


class TestLocalPathIterator(unittest.TestCase):
    def setUp(self):
        # Создаем временную директорию для тестов
        self.test_dir = tempfile.TemporaryDirectory()

        # Создаем файлы в этой директории
        self.file1 = os.path.join(self.test_dir.name, "file1.log")
        self.file2 = os.path.join(self.test_dir.name, "file2.txt")

        # Создаем лог-файл с данными
        with open(self.file1, "w") as f:
            f.write("line1\nline2\nline3")

        # Создаем текстовый файл без данных
        with open(self.file2, "w") as f:
            f.write("")

    def tearDown(self):
        # Удаляем временную директорию после тестов
        self.test_dir.cleanup()

    def test_local_path_iterator_reading(self):
        # Создаем итератор с паттерном поиска *.log в тестовой директории
        iterator = LocalPathIterator(os.path.join(self.test_dir.name, "*.log"))

        # Проходим по итератору
        lines = list(iterator)

        # Проверяем, что строки из файла file1.log были корректно извлечены
        self.assertEqual(lines, ["line1", "line2", "line3"])

    def test_local_path_iterator_no_files(self):
        # Создаем итератор с паттерном, который не должен находить файлов (например, *.md)
        iterator = LocalPathIterator(os.path.join(self.test_dir.name, "*.md"))

        # Проходим по итератору
        lines = list(iterator)

        # Проверяем, что итератор не нашел файлов и ничего не вернул
        self.assertEqual(lines, [])
