import unittest
from unittest.mock import patch
import numpy as np
from src.databases.log_data import LogData
from src.parser_process.log_processor import LogParserProcessor


class TestLogStatistics(unittest.TestCase):
    @patch(
        "src.iterators.local_path_iterator.LocalPathIterator.__iter__",
        return_value=iter(
            [
                '127.0.0.1 - - [09/Nov/2024:09:00:00 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"',
                '127.0.0.2 - - [09/Nov/2024:09:05:00 +0000] "POST /login HTTP/1.1" 200 5678 "-" "Mozilla/5.0"',
                '127.0.0.3 - - [09/Nov/2024:09:40:00 +0000] "GET /about.html HTTP/1.1" 404 2345 "-" "Mozilla/5.0"',
                '127.0.0.4 - - [09/Nov/2024:10:15:00 +0000] "GET /contact.html HTTP/1.1" 200 3456 "-" "Mozilla/5.0"',
                '127.0.0.5 - - [09/Nov/2024:10:20:00 +0000] "DELETE /delete HTTP/1.1" 500 6789 "-" "Mozilla/5.0"',
            ]
        ),
    )
    def test_calculate_statistics(self, mock_file):
        # Подготовка данных
        log_data = LogData(repr_format="markdown")
        processor = LogParserProcessor(log_data)

        # Запуск обработки логов
        processor.process("mock_path")

        # Проверка общего количества запросов
        self.assertEqual(log_data.total_requests_cnt, 5)

        # Проверка статистики по типам запросов
        self.assertEqual(log_data.request_types["GET"], 3)
        self.assertEqual(log_data.request_types["POST"], 1)
        self.assertEqual(log_data.request_types["DELETE"], 1)

        # Проверка статистики по кодам ответа
        self.assertEqual(log_data.response_codes_statistics["200"], 3)
        self.assertEqual(log_data.response_codes_statistics["404"], 1)
        self.assertEqual(log_data.response_codes_statistics["500"], 1)

        # Проверка статистики по источникам
        self.assertEqual(log_data.sources_statistics["/index.html"], 1)
        self.assertEqual(log_data.sources_statistics["/login"], 1)
        self.assertEqual(log_data.sources_statistics["/about.html"], 1)
        self.assertEqual(log_data.sources_statistics["/contact.html"], 1)
        self.assertEqual(log_data.sources_statistics["/delete"], 1)

        # Проверка статистики по IP-адресам
        self.assertEqual(log_data.ip_statistics["127.0.0.1"], 1)
        self.assertEqual(log_data.ip_statistics["127.0.0.2"], 1)
        self.assertEqual(log_data.ip_statistics["127.0.0.3"], 1)
        self.assertEqual(log_data.ip_statistics["127.0.0.4"], 1)
        self.assertEqual(log_data.ip_statistics["127.0.0.5"], 1)

        # Проверка подсчета среднего размера ответа
        average_size = sum(log_data.response_sizes) / len(log_data.response_sizes)
        self.assertEqual(average_size, 3900.4)

        # Проверка 95-го перцентиля размера ответа
        log_data.response_sizes.sort()
        percentile_95 = np.percentile(sorted(log_data.response_sizes), 95)
        self.assertEqual(percentile_95, 6566.8)

    @patch(
        "src.iterators.local_path_iterator.LocalPathIterator.__iter__",
        return_value=iter(
            [
                '127.0.0.1 - - [09/Nov/2024:09:00:00 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"',
                '127.0.0.2 - - [09/Nov/2024:09:05:00 +0000] "POST /login HTTP/1.1" 200 5678 "-" "Mozilla/5.0"',
                '127.0.0.3 - - [09/Nov/2024:09:40:00 +0000] "GET /about.html HTTP/1.1" 404 2345 "-" "Mozilla/5.0"',
            ]
        ),
    )
    def test_time_filter_statistics(self, mock_file):
        # Подготовка данных с фильтрацией по времени
        log_data = LogData(repr_format="markdown")
        processor = LogParserProcessor(log_data)

        # Запуск обработки логов с фильтрацией по времени
        processor.process("mock_path")

        # Проверка, что количество запросов за заданный интервал времени верное
        self.assertEqual(log_data.total_requests_cnt, 3)

    @patch(
        "src.iterators.local_path_iterator.LocalPathIterator.__iter__",
        return_value=iter(
            [
                '127.0.0.1 - - [09/Nov/2024:09:00:00 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"\n',
                '127.0.0.2 - - [09/Nov/2024:09:05:00 +0000] "POST /login HTTP/1.1" 200 5678 "-" "Mozilla/5.0"\n',
                '127.0.0.3 - - [09/Nov/2024:09:40:00 +0000] "GET /about.html HTTP/1.1" 404 2345 "-" "Mozilla/5.0"\n',
                '127.0.0.4 - - [09/Nov/2024:10:15:00 +0000] "GET /contact.html HTTP/1.1" 200 3456 "-" "Mozilla/5.0"\n',
            ]
        ),
    )
    def test_error_url_statistics(self, mock_file):
        # Подготовка данных для ошибки
        log_data = LogData(
            from_date="2024-11-09T09:00:00",
            to_date="2024-11-09T10:30:00",
            repr_format="markdown",
        )
        processor = LogParserProcessor(log_data)

        # Запуск обработки логов
        processor.process("mock_path")

        # Проверка статистики по ошибкам
        self.assertIn("/about.html", log_data.error_urls)
        self.assertNotIn("/index.html", log_data.error_urls)
