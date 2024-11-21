from src.databases.log_data import LogData


class Saver:
    def __init__(self, log_data: LogData):
        self.log_data = log_data

    def save(self, path: str) -> None:
        if self.log_data.repr_format == "markdown":
            with open(path + ".md", "w", encoding="utf-8") as f:
                f.writelines(self.log_data.__repr__())
        else:
            with open(path + ".adoc", "w", encoding="utf-8") as f:
                f.writelines(self.log_data.__repr__())
