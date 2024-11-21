from src.parser_process.initialize_cli import initialize_cli
from src.databases.log_data import LogData
from src.parser_process.log_processor import LogParserProcessor
from src.saver.saver import Saver


def main() -> None:
    parser = initialize_cli()

    args_from_cmd = parser.parse_args()

    log_data = LogData(
        from_date=args_from_cmd.from_date,
        to_date=args_from_cmd.to_date,
        repr_format=args_from_cmd.format,
    )

    log_parser_processor = LogParserProcessor(
        log_data, args_from_cmd.filter_field, args_from_cmd.filter_value
    )

    log_parser_processor.process(args_from_cmd.path)

    saver = Saver(log_data)
    saver.save("src/output/out")

    print(log_data)


if __name__ == "__main__":
    main()
