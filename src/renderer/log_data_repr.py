import numpy as np
from http import HTTPStatus


class LogDataRepr:
    """Класс для репрезентации данных о логах в различных форматах"""

    def __init__(self, log_data):
        self.log_data = log_data
        self.from_date_str = log_data.from_date if log_data.from_date else "-"
        self.to_date_str = log_data.to_date if log_data.to_date else "-"

    @property
    def _name_str(self) -> str:
        return ", ".join(self.log_data.file_names)

    @property
    def _total_req_amount(self) -> str:
        return f"{self.log_data.total_requests_cnt:_}"

    @property
    def _aver_response(self) -> str:
        if self.log_data.total_requests_cnt > 0:
            return f"{np.mean(self.log_data.response_sizes):_.2f}"
        return "-"

    @property
    def _percent_95(self) -> str:
        if self.log_data.response_sizes:
            return f"{np.percentile(sorted(self.log_data.response_sizes), 95):_.2f}"
        return "-"

    def _prepare(self) -> None:
        self.log_data.response_codes_statistics = dict(
            sorted(self.log_data.response_codes_statistics.items())
        )

    def get_repr(self, format_type: str) -> str:
        self._prepare()
        match format_type:
            case "markdown":
                return self._generate_markdown_repr()
            case "adoc":
                return self._generate_adoc_repr()
            case _:
                raise ValueError("Unknown format type")

    @staticmethod
    def _calculate_column_width(column_data, min_width: int = 2) -> int:
        return max(len(str(data)) for data in column_data) + min_width

    def _generate_markdown_repr(self) -> str:
        # ширина 2ой колонки основной информации
        general_inform_second_col_width = (
            max(
                len(self._name_str),
                len(self.from_date_str),
                len(self.to_date_str),
                len(self._total_req_amount),
                len(self._aver_response),
                len(self._percent_95),
                len("Значение"),
            )
            + 1
        )

        # ширина 1ой колонки таблицы с ресурсами
        req_res_first_col_width = self._calculate_column_width(
            [*self.log_data.sources_statistics.keys(), "Ресурс"], 2
        )

        # ширина 2ой колонки таблицы с ресурсами
        req_res_second_col_width = self._calculate_column_width(
            [*self.log_data.sources_statistics.values(), "Количество"]
        )

        # сама таблица с ресурсами
        sources_table = "".join(
            f"|{f'`{source}`':^{req_res_first_col_width}}|{amount:>{req_res_second_col_width}_}|\n"
            for source, amount in self.log_data.sources_statistics.items()
        )

        # ширина 1ой колонки таблицы с кодами ответа
        code_first_col_width = 5
        # ширина 2ой колонки таблицы с кодами ответа
        code_second_col_width = self._calculate_column_width(
            [
                self._get_status_name(code)
                for code in self.log_data.response_codes_statistics.keys()
            ]
            + ["Имя"],
            2,
        )
        # ширина 3ей колонки таблицы с кодами ответа
        code_third_col_width = self._calculate_column_width(
            [*self.log_data.response_codes_statistics.values(), "Количество"], 2
        )
        # сама таблица с кодами ответа
        codes_table = "".join(
            f"|{code:^5}|{self._get_status_name(code):^{code_second_col_width}}|{cnt:>{code_third_col_width}_}|\n"
            for code, cnt in self.log_data.response_codes_statistics.items()
        )

        # ширина 1ой колонки таблицы с типами запросов
        source_first_col_width = self._calculate_column_width(
            [*self.log_data.request_types.keys(), "Тип запроса"], 2
        )

        # ширина 2ой колонки таблицы с типами запросов
        source_second_col_width = self._calculate_column_width(
            [*self.log_data.request_types.values(), "Количество"], 2
        )

        # сама таблица с типами запросов
        source_table = "\n".join(
            f"|{request:^{source_first_col_width}}| {cnt:{source_second_col_width - 1}_}|"
            for request, cnt in self.log_data.request_types.items()
        )

        # ширина 1ой колонки таблицы с IP-адресами
        ip_stat_first_col_width = self._calculate_column_width(
            [*self.log_data.ip_statistics.keys(), "IP-адрес"], 2
        )
        # ширина 2ой колонки таблицы с IP-адресами
        ip_stat_second_col_width = self._calculate_column_width(
            [*self.log_data.ip_statistics.values(), "Кол-во запросов"], 2
        )

        # сортировка по количеству запросов
        self.log_data.ip_statistics = dict(
            sorted(
                self.log_data.ip_statistics.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        )

        # сама таблица с IP-адресами
        ip_statistics_table = "\n".join(
            f"|{ip:^{ip_stat_first_col_width}}|{cnt:>{ip_stat_second_col_width}_}|"
            for ip, cnt in self.log_data.ip_statistics.items()
        )

        # ширина 1ой колонки таблицы с URL, вызвавшими ошибки
        error_url = ", ".join(self.log_data.error_urls)

        return (
            f"#### Общая информация\n\n"
            f"|{'Метрика':^23}|{'Значение':>{general_inform_second_col_width}}|\n"
            f"|:{'-' * 21}:|{'-' * (general_inform_second_col_width - 1)}:|\n"
            f"|{'Файл(-ы)':^23}|{self._name_str:>{general_inform_second_col_width}}|\n"
            f"|{'Начальная дата':^23}|{self.from_date_str:>{general_inform_second_col_width}}|\n"
            f"|{'Конечная дата':^23}|{self.to_date_str:>{general_inform_second_col_width}}|\n"
            f"|{'Количество запросов':^23}|{self._total_req_amount:>{general_inform_second_col_width}}|\n"
            f"|{'Средний размер ответа':^23}|{self._aver_response:>{general_inform_second_col_width}}|\n"
            f"|{'95p размера ответа':^23}|{self._percent_95:>{general_inform_second_col_width}}|\n"
            f"\n#### Запрашиваемые ресурсы\n\n"
            f"|{'Ресурс':^{req_res_first_col_width}}|{'Количество':>{req_res_second_col_width}}|\n"
            f"|:{'-' * (req_res_first_col_width - 2)}:|{'-' * (req_res_second_col_width - 1)}:|\n"
            f"{sources_table}"
            f"\n#### Коды ответа\n\n"
            f"|{'Код':^{code_first_col_width}}|{'Имя':^{code_second_col_width}}|{'Количество':>{code_third_col_width}}|\n"
            f"|:{'-' * (code_first_col_width - 2)}:|:{'-' * (code_second_col_width - 2)}:|{'-' * (code_third_col_width - 1)}:|\n"
            f"{codes_table}"
            f"\n#### Статистика по запросам\n\n"
            f"|{'Тип запроса':^{source_first_col_width}}|{'Количество':^{source_second_col_width}}|\n"
            f"|:{'-' * (source_first_col_width - 2)}:|:{'-' * (source_second_col_width - 2)}:|\n"
            f"{source_table}\n"
            f"\n#### Статистика по IP-адресам\n\n"
            f"|{'IP-адрес':^{ip_stat_first_col_width}}|{'Кол-во запросов':>{ip_stat_second_col_width}}|\n"
            f"|:{'-' * (ip_stat_first_col_width - 2)}:|:{'-' * (ip_stat_second_col_width - 2)}:|\n"
            f"{ip_statistics_table}\n"
            f"\n#### Ресурсы с ошибками\n\n"
            f"{error_url}"
        )

    def _generate_adoc_repr(self) -> str:
        # Секция общей информации
        adoc_output = (
            f"=== Общая информация\n\n"
            f"* **Файлы:** {', '.join(self.log_data.file_names)}\n"
            f"* **Начальная дата:** {self.from_date_str}\n"
            f"* **Конечная дата:** {self.to_date_str}\n"
            f"* **Количество запросов:** {self.log_data.total_requests_cnt:_}\n"
            f"* **Средний размер ответа:** {self._aver_response}\n"
            f"* **95-й перцентиль размера ответа:** {self._percent_95}\n\n"
        )

        # Секция с запрашиваемыми ресурсами
        adoc_output += "=== Запрашиваемые ресурсы\n\n"
        adoc_output += '[options="header"]\n|===\n|Ресурс |Количество\n'
        for source, amount in self.log_data.sources_statistics.items():
            adoc_output += f"|`{source}` |{amount:_}\n"
        adoc_output += "|===\n\n"

        # Секция с кодами ответа
        adoc_output += "=== Коды ответа\n\n"
        adoc_output += '[options="header"]\n|===\n|Код |Имя |Количество\n'
        for code, count in self.log_data.response_codes_statistics.items():
            adoc_output += f"|{code} |{self._get_status_name(code)} |{count:_}\n"
        adoc_output += "|===\n\n"

        # Секция со статистикой запросов
        adoc_output += "=== Статистика по запросам\n\n"
        adoc_output += '[options="header"]\n|===\n|Тип запроса |Количество\n'
        for request, count in self.log_data.request_types.items():
            adoc_output += f"|{request} |{count:_}\n"
        adoc_output += "|===\n\n"

        # Секция со статистикой по IP-адресам
        adoc_output += "=== Статистика по IP-адресам\n\n"
        adoc_output += '[options="header"]\n|===\n|IP-адрес |Количество запросов\n'
        for ip, count in self.log_data.ip_statistics.items():
            adoc_output += f"|{ip} |{count:_}\n"
        adoc_output += "|===\n\n"

        # Секция с URL, вызвавшими ошибки
        adoc_output += "=== Ресурсы с ошибками\n\n"
        adoc_output += ", ".join(f"`{url}`" for url in self.log_data.error_urls)

        return adoc_output

    @staticmethod
    # Функция для получения имени статуса с использованием HTTPStatus
    def _get_status_name(code: str) -> str:
        try:
            status = HTTPStatus(int(code))
            return status.phrase
        except ValueError:
            return "Unknown"
