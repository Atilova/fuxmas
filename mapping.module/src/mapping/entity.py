from uuid import NAMESPACE_URL, UUID, uuid4, uuid5
from dataclasses import dataclass, field
from pathlib import Path

from src.mapping.enums import Strategy, Status


@dataclass(kw_only=True)
class StrategyEntity:
    id: UUID = field(default_factory=uuid4)
    status: Status
    total_pixels: int
    strategy: Strategy
    positions: list[tuple[int, int]]

    @property
    def path_dir(self) -> Path:
        return Path(str(self.id))


@dataclass(kw_only=True)
class ExposedFileEntity:
    file_path: Path
    id: UUID = field(init=False)

    def __post_init__(self):
        self.id = uuid5(NAMESPACE_URL, str(self.file_path))
