from dataclasses import dataclass, field
from collections import defaultdict
from src.renderer.log_data_repr import LogDataRepr


@dataclass
class LogData:
    """Класс для хранения статистики по логам"""

    total_requests_cnt: int = 0
    sources_statistics: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    response_codes_statistics: dict[str, int] = field(
        default_factory=lambda: defaultdict(int)
    )
    response_sizes: list[int] = field(default_factory=list)
    request_types: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    ip_statistics: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    error_urls: set[str] = field(default_factory=set)
    file_names: list[str] = field(default_factory=list)
    from_date: str | None = field(default=None, init=True)
    to_date: str | None = field(default=None, init=True)
    repr_format: str = field(default="markdown", init=True)

    def __repr__(self):
        return LogDataRepr(self).get_repr(self.repr_format)
