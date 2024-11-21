from src.iterators.url_path_iterator import URLPathIterator
from src.iterators.local_path_iterator import LocalPathIterator
from src.databases.log_data import LogData

import re
from datetime import datetime, timezone
from fnmatch import fnmatch


class LogParserProcessor:
    """
    Класс реализует процесс подсчета данных необходимых для статистики по логам

    - Подсчитывает общее количество запросов
    - Определяет наиболее часто запрашиваемые ресурсы
    - Определяет наиболее часто встречающиеся коды ответа
    - Рассчитывает средний размер ответа сервера
    - Рассчитывает 95% перцентиль размера ответа сервера

    Дополнительно:
    - Количество запросов каждого типа (GET, POST и т.д.)
    - Статистика по IP-адресам
    - Список всех URL, которые вернули ошибку (коды ответа 4xx или 5xx)
    """

    def __init__(
        self,
        log_data: LogData,
        filter_field: str | None = None,
        filter_value: str | None = None,
    ):
        self.log_data: LogData = log_data
        self.filter_field: str | None = filter_field
        self.filter_value: str | None = filter_value

    def __post_init__(self):
        if self.filter_field is not None:
            self.filter_field = self.filter_field.lower()
        if self.filter_value is not None:
            self.filter_value = self.filter_value.lower()

    @staticmethod
    # Функция для парсинга строки лога
    def parse_log_line(line: str) -> dict[str, str] | None:
        # Регулярное выражение для разбора строк логов
        log_pattern = re.compile(
            r"(?P<remote_addr>\S+) "  # IP адрес
            r"- (?P<remote_user>\S*) "  # Пользователь (или "-")
            r"\[(?P<time_local>[^\]]+)\] "  # Время
            r'"(?P<method>\S+) (?P<source>\S+) (?P<protocol>\S+)" '  # Запрос (метод, источник, протокол)
            r"(?P<status>\d{3}) "  # Статус ответа
            r"(?P<body_bytes_sent>\d+) "  # Количество байт
            r'"(?P<http_referer>[^"]*)" '  # Реферер
            r'"(?P<http_user_agent>[^"]*)"'  # User-Agent
        )
        match = log_pattern.match(line)
        if match:
            return match.groupdict()

    @staticmethod
    def get_iterator(path: str) -> URLPathIterator | LocalPathIterator:
        if path.startswith("http"):
            # Для URL возвращаем URLPathIterator
            return URLPathIterator(path)
        else:
            # Для локального пути используем LocalPathIterator
            return LocalPathIterator(path)

    @staticmethod
    # Преобразование строковых дат в объекты datetime (если задано)
    def parse_iso8601(date_str: str | None) -> datetime | None:
        if date_str:
            # Создаем datetime объект без смещения, добавляем UTC смещение
            return datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)

    def _matches_time_filter(self, parsed_log: dict[str, str]) -> bool:
        start_time = self.parse_iso8601(self.log_data.from_date)
        end_time = self.parse_iso8601(self.log_data.to_date)
        log_time = datetime.strptime(parsed_log["time_local"], "%d/%b/%Y:%H:%M:%S %z")

        if start_time is not None and log_time < start_time:
            return False
        if end_time is not None and log_time > end_time:
            return False
        return True

    def _matches_filter(self, parsed_log: dict[str, str]) -> bool:
        field_value = parsed_log.get(self.filter_field)
        if field_value is None:
            return False
        return fnmatch(field_value, self.filter_value)

    def check_log(self, parsed_log: dict[str, str]) -> bool:
        if (
            self.filter_field is not None
            and self.filter_value is not None
            and not self._matches_filter(parsed_log)
        ):
            return False
        return self._matches_time_filter(parsed_log)

    def process(self, path: str) -> None:
        iterator = self.get_iterator(path)
        self.log_data.file_names = iterator.files

        for line in iterator:
            parsed = self.parse_log_line(line)
            if parsed and self.check_log(parsed):
                self.log_data.total_requests_cnt += 1
                self.log_data.sources_statistics[parsed["source"]] += 1
                self.log_data.response_codes_statistics[parsed["status"]] += 1
                self.log_data.response_sizes.append(int(parsed["body_bytes_sent"]))

                self.log_data.request_types[parsed["method"]] += 1
                self.log_data.ip_statistics[parsed["remote_addr"]] += 1
                if parsed["status"].startswith("4") or parsed["status"].startswith("5"):
                    self.log_data.error_urls.add(parsed["source"])
