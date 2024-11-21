from argparse import ArgumentParser


def initialize_cli() -> ArgumentParser:
    """Получить парсер аргументов командной строки"""
    cli_parser = ArgumentParser(
        prog="cli_parser", description="Выводит статистику по логам NGINX."
    )
    cli_parser.add_argument(
        "--path",
        type=str,
        metavar="DIRECTORY/URL",
        help="Путь к директории/url с файлами логов",
        required=True,
    )
    cli_parser.add_argument(
        "--from",
        type=str,
        metavar="FROM_DATE",
        help="Начальная дата в формате ISO8601",
        dest="from_date",
    )
    cli_parser.add_argument(
        "--to",
        type=str,
        metavar="TO_DATE",
        help="Конечная дата в формате ISO8601",
        dest="to_date",
    )
    cli_parser.add_argument(
        "--format",
        choices=["markdown", "adoc"],
        type=str.lower,
        metavar="FORMAT",
        default="markdown",
        help="Формат отображения статистики (markdown или adoc)",
    )

    cli_parser.add_argument(
        "--filter-field",
        type=str,
        metavar="FIELD",
        help="Поле для фильтрации (например, agent, method)",
    )
    cli_parser.add_argument(
        "--filter-value",
        type=str,
        metavar="VALUE",
        help="Значение для фильтрации (например, Mozilla*, GET)",
    )

    return cli_parser
