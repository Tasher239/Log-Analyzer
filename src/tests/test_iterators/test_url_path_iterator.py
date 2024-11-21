import unittest
from unittest.mock import patch
from src.iterators.url_path_iterator import URLPathIterator


class TestURLPathIterator(unittest.TestCase):
    @patch("requests.get")
    def test_url_path_iterator(self, mock_get):
        # Мокируем response для URL
        mock_response = mock_get.return_value
        mock_response.iter_lines.return_value = ["line1", "line2"]

        iterator = URLPathIterator("http://example.com/logfile")
        lines = list(iterator)

        # Проверка правильности работы итератора
        self.assertEqual(lines, ["line1", "line2"])
        mock_get.assert_called_once_with("http://example.com/logfile", stream=True)
