from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from src.mapping.enums import Strategy, Status
from src.mapping.interfaces import IFile
from src.mapping.entity import StrategyEntity


class StrategyInit(BaseModel):
    model_config = ConfigDict({
        "arbitrary_types_allowed": True
    })

    total_pixels: int
    strategy: Strategy
    file: IFile


class StrategyInitResult(BaseModel):
    id: UUID


class StrategyRead(BaseModel):
    id: UUID


class StrategyReadResult(BaseModel):
    id: UUID
    status: Status
    total_pixels: int
    strategy: Strategy
    positions: list[tuple[int, int]]

    @classmethod
    def from_entity(cls, entity: StrategyEntity):
        return cls(
            id=entity.id,
            status=entity.status,
            total_pixels=entity.total_pixels,
            strategy=entity.strategy,
            positions=entity.positions,
        )


class StrategyGrayLabelTry(BaseModel):
    class Options(BaseModel):
        use_tone_pre_processing: bool = True

        use_post_filter: bool = True
        post_filter_leds_margin: int = 10

        min_distance: int = Field(14, ge=10, le=30)
        quality_levels: float = Field(0.02, ge=0.01, le=0.3)

    id: UUID
    options: Options = Field(default_factory=Options)


class StrategyGrayLabelTryResult(BaseModel):
    frame_url: str
    led_positions: list[tuple[int, int]]


class StrategyGrayLabelContinue(BaseModel):
    id: UUID
    led_positions: list[tuple[int, int]]


class StrategyGrayLabelContinueResult(BaseModel):
    total: int
    positions: list[tuple[int, int]]
