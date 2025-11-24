from uuid import UUID
from dataclasses import dataclass
from pathlib import Path

from src.mapping.enums import Strategy, Status


@dataclass(kw_only=True)
class StrategyEntity:
    id: UUID
    status: Status
    total_pixels: int
    strategy: Strategy
    file_path: Path
    positions: list[tuple[int, int]]
