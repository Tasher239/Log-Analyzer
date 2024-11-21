import unittest
from unittest.mock import patch, mock_open
from src.parser_process.log_processor import LogParserProcessor
from src.databases.log_data import LogData


class TestLogParserProcessor(unittest.TestCase):

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='127.0.0.1 - - [09/Nov/2024:10:00:00 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"',
    )
    def test_parse_log_line(self, mock_file):
        log_data = LogData(repr_format="markdown")
        processor = LogParserProcessor(log_data)

        # Тестирование парсинга строки лога
        line = '127.0.0.1 - - [09/Nov/2024:10:00:00 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"'
        parsed = processor.parse_log_line(line)

        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["remote_addr"], "127.0.0.1")
        self.assertEqual(parsed["status"], "200")
        self.assertEqual(parsed["method"], "GET")
        self.assertEqual(parsed["source"], "/index.html")
        self.assertEqual(parsed["protocol"], "HTTP/1.1")

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=(
            '127.0.0.1 - - [09/Nov/2024:10:00:00 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"\n'
            '127.0.0.2 - - [09/Nov/2024:10:05:00 +0000] "POST /login HTTP/1.1" 200 5678 "-" "Mozilla/5.0"\n'
            '127.0.0.3 - - [09/Nov/2024:10:10:00 +0000] "GET /about.html HTTP/1.1" 404 2345 "-" "Mozilla/5.0"\n'
            '127.0.0.4 - - [09/Nov/2024:10:15:00 +0000] "GET /contact.html HTTP/1.1" 200 3456 "-" "Mozilla/5.0"\n'
            '127.0.0.5 - - [09/Nov/2024:10:20:00 +0000] "DELETE /delete HTTP/1.1" 500 6789 "-" "Mozilla/5.0"'
        ),
    )
    def test_parse_log_lines(self, mock_file):
        log_data = LogData(repr_format="markdown")
        processor = LogParserProcessor(log_data)

        # Тестирование парсинга нескольких строк логов
        log_lines = [
            '127.0.0.1 - - [09/Nov/2024:10:00:00 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"',
            '127.0.0.2 - - [09/Nov/2024:10:05:00 +0000] "POST /login HTTP/1.1" 200 5678 "-" "Mozilla/5.0"',
            '127.0.0.3 - - [09/Nov/2024:10:10:00 +0000] "GET /about.html HTTP/1.1" 404 2345 "-" "Mozilla/5.0"',
            '127.0.0.4 - - [09/Nov/2024:10:15:00 +0000] "GET /contact.html HTTP/1.1" 200 3456 "-" "Mozilla/5.0"',
            '127.0.0.5 - - [09/Nov/2024:10:20:00 +0000] "DELETE /delete HTTP/1.1" 500 6789 "-" "Mozilla/5.0"',
        ]

        for line in log_lines:
            parsed = processor.parse_log_line(line)
            self.assertIsNotNone(parsed)
            self.assertIn("remote_addr", parsed)
            self.assertIn("status", parsed)
            self.assertIn("method", parsed)
            self.assertIn("source", parsed)
            self.assertIn("protocol", parsed)

    def test_check_log_with_filter(self):
        log_data = LogData(
            from_date="2024-11-09T09:00:00",
            to_date="2024-11-09T11:00:00",
            repr_format="markdown",
        )
        processor = LogParserProcessor(
            log_data, filter_field="status", filter_value="200"
        )

        # Тестирование фильтрации по полю и значению
        parsed_log = {
            "time_local": "09/Nov/2024:10:00:00 +0000",
            "status": "200",
            "request": "GET /index.html HTTP/1.1",
            "remote_addr": "127.0.0.1",
            "body_bytes_sent": "1234",
            "http_referer": "-",
            "http_user_agent": "Mozilla/5.0",
        }
        result = processor.check_log(parsed_log)
        self.assertTrue(result)

        parsed_log["status"] = "404"
        result = processor.check_log(parsed_log)
        self.assertFalse(result)

    @patch(
        "src.iterators.local_path_iterator.LocalPathIterator.__iter__",
        return_value=iter(
            [
                '127.0.0.1 - - [09/Nov/2024:10:00:00 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"',
                '127.0.0.2 - - [09/Nov/2024:10:05:00 +0000] "POST /login HTTP/1.1" 200 5678 "-" "Mozilla/5.0"',
                '127.0.0.3 - - [09/Nov/2024:10:10:00 +0000] "GET /about.html HTTP/1.1" 404 2345 "-" "Mozilla/5.0"',
                '127.0.0.4 - - [09/Nov/2024:10:15:00 +0000] "GET /contact.html HTTP/1.1" 200 3456 "-" "Mozilla/5.0"',
                '127.0.0.5 - - [09/Nov/2024:10:20:00 +0000] "DELETE /delete HTTP/1.1" 500 6789 "-" "Mozilla/5.0"',
            ]
        ),
    )
    def test_process(self, mock_file):
        log_data = LogData(repr_format="markdown")
        processor = LogParserProcessor(log_data)

        # Тестирование обработки логов
        processor.process("test_path")

        # Проверка корректности обработки логов
        self.assertEqual(log_data.total_requests_cnt, 5)
        self.assertEqual(log_data.sources_statistics["/index.html"], 1)
        self.assertEqual(log_data.sources_statistics["/login"], 1)
        self.assertEqual(log_data.sources_statistics["/about.html"], 1)
        self.assertEqual(log_data.sources_statistics["/contact.html"], 1)
        self.assertEqual(log_data.sources_statistics["/delete"], 1)
        self.assertEqual(log_data.response_codes_statistics["200"], 3)
        self.assertEqual(log_data.response_codes_statistics["404"], 1)
        self.assertEqual(log_data.response_codes_statistics["500"], 1)
        self.assertEqual(len(log_data.response_sizes), 5)
        self.assertEqual(log_data.request_types["GET"], 3)
        self.assertEqual(log_data.request_types["POST"], 1)
        self.assertEqual(log_data.request_types["DELETE"], 1)
        self.assertEqual(log_data.ip_statistics["127.0.0.1"], 1)
        self.assertEqual(log_data.ip_statistics["127.0.0.2"], 1)
        self.assertEqual(log_data.ip_statistics["127.0.0.3"], 1)
        self.assertEqual(log_data.ip_statistics["127.0.0.4"], 1)
        self.assertEqual(log_data.ip_statistics["127.0.0.5"], 1)

    @patch(
        "src.iterators.local_path_iterator.LocalPathIterator.__iter__",
        return_value=iter(
            [
                '127.0.0.1 - - [09/Nov/2024:09:00:00 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"\n',
                '127.0.0.2 - - [09/Nov/2024:09:30:00 +0000] "POST /login HTTP/1.1" 200 5678 "-" "Mozilla/5.0"\n',
                '127.0.0.3 - - [10/Nov/2024:10:00:00 +0000] "GET /about.html HTTP/1.1" 404 2345 "-" "Mozilla/5.0"\n',
                '127.0.0.4 - - [10/Dec/2024:10:15:00 +0000] "GET /contact.html HTTP/1.1" 200 3456 "-" "Mozilla/5.0"\n',
                '127.0.0.5 - - [11/Jan/2024:20:30:00 +0000] "DELETE /delete HTTP/1.1" 500 6789 "-" "Mozilla/5.0"',
            ]
        ),
    )
    def test_check_log_with_time_filter(self, mock_file):
        log_data = LogData(
            from_date="2024-11-09T09:30:00",
            to_date="2024-11-10T10:30:00",
            repr_format="markdown",
        )
        processor = LogParserProcessor(log_data)
        processor.process("test_path")

        # Логи, которые будут в пределах временного интервала:
        parsed_log_1 = {
            "time_local": "09/Nov/2024:09:00:00 +0000",
            "status": "200",
            "request": "GET /index.html HTTP/1.1",
            "remote_addr": "127.0.0.1",
            "body_bytes_sent": "1234",
            "http_referer": "-",
            "http_user_agent": "Mozilla/5.0",
        }
        parsed_log_2 = {
            "time_local": "09/Nov/2024:09:30:00 +0000",
            "status": "200",
            "request": "POST /login HTTP/1.1",
            "remote_addr": "127.0.0.2",
            "body_bytes_sent": "5678",
            "http_referer": "-",
            "http_user_agent": "Mozilla/5.0",
        }
        parsed_log_3 = {
            "time_local": "10/Nov/2024:10:00:00 +0000",
            "status": "200",
            "request": "GET /contact.html HTTP/1.1",
            "remote_addr": "127.0.0.4",
            "body_bytes_sent": "3456",
            "http_referer": "-",
            "http_user_agent": "Mozilla/5.0",
        }
        parsed_log_4 = {
            "time_local": "10/Dec/2024:10:15:00 +0000",
            "status": "200",
            "request": "GET /contact.html HTTP/1.1",
            "remote_addr": "127.0.0.4",
            "body_bytes_sent": "3456",
            "http_referer": "-",
            "http_user_agent": "Mozilla/5.0",
        }
        parsed_log_5 = {
            "time_local": "11/Jan/2024:20:30:00 +0000",
            "status": "200",
            "request": "GET /contact.html HTTP/1.1",
            "remote_addr": "127.0.0.4",
            "body_bytes_sent": "3456",
            "http_referer": "-",
            "http_user_agent": "Mozilla/5.0",
        }

        # Тестирование фильтрации по времени (два лог-записи будут в пределах интервала)
        result_1 = processor.check_log(parsed_log_1)  # Это будет FALSE
        result_2 = processor.check_log(parsed_log_2)  # Это будет TRUE
        result_3 = processor.check_log(parsed_log_3)  # Это будет TRUE
        result_4 = processor.check_log(parsed_log_4)  # Это будет FALSE
        result_5 = processor.check_log(parsed_log_5)  # Это будет FALSE

        self.assertFalse(result_1)
        self.assertTrue(result_2)
        self.assertTrue(result_3)
        self.assertFalse(result_4)
        self.assertFalse(result_5)

        self.assertEqual(log_data.total_requests_cnt, 2)
        self.assertEqual(log_data.sources_statistics["/login"], 1)
        self.assertEqual(log_data.sources_statistics["/about.html"], 1)
        self.assertEqual(log_data.response_codes_statistics["200"], 1)
        self.assertEqual(log_data.response_codes_statistics["404"], 1)
        self.assertEqual(len(log_data.response_sizes), 2)
        self.assertEqual(log_data.request_types["GET"], 1)
        self.assertEqual(log_data.request_types["POST"], 1)
        self.assertEqual(log_data.ip_statistics["127.0.0.2"], 1)
        self.assertEqual(log_data.ip_statistics["127.0.0.3"], 1)


if __name__ == "__main__":
    unittest.main()
