from pathlib import Path
from uuid import UUID

from src.mapping.enums import FileMIME, Strategy, Status
from src.mapping.interfaces import IStorage, IRepository, IExposeFilePort
from src.mapping.entity import StrategyEntity
from src.mapping.dto import (
   StrategyGrayLabelTry,
   StrategyGrayLabelTryResult,
   StrategyGrayLabelContinue,
   StrategyGrayLabelContinueResult
)
from src.mapping.exceptions import (
    StrategyNotFound,
    StrategyUnapplicable,
    GrayLabelMappingException,
)
from pkg.file import format_fullname, join_path_parts
from pkg.graylabel import (
    MappingFunctionException,
    clip_video,
    encode_frame,
    decode_frame,
    darken_tone,
    detect_pixels,
    score_pixels,
    read_labels,
    get_n_unique_frames_required,
)


_FRAMES_DIR = "frames"
_FRAME_EXT = ".jpg"
_BASE_FRAME_FULLNAME = f"0{_FRAME_EXT}"


class GrayLabelStrategyPort:
    def __init__(
        self,
        *,
        storage: IStorage,
        repository: IRepository,
        expose_file_port: IExposeFilePort,
    ):
        self._storage = storage
        self._repository = repository
        self._expose_file_port = expose_file_port

    def is_supported_mime(self, mime: FileMIME) -> bool:
        return mime in (FileMIME.MP4, FileMIME.MOV, FileMIME.AVI)

    async def init(
        self,
        entity: StrategyEntity,
        downloaded_file_path: Path,
    ):
        try:
            for frame_idx, frame, in clip_video(
                file_path=self._storage.get_local_filesystem_path(
                    downloaded_file_path,
                ),
                n_pixels=entity.total_pixels,
                pattern_interval=2,
            ):
                buffer, ext = encode_frame(frame, _FRAME_EXT)
                await self._storage.save_buffer(
                    file_path=join_path_parts(
                        entity.path_dir, _FRAMES_DIR, format_fullname(frame_idx, ext),
                    ),
                    buffer=buffer,
                )
        except MappingFunctionException as exc:
            await self._storage.delete(entity.path_dir)
            raise GrayLabelMappingException.from_exc(exc) from exc

        await self._storage.delete(downloaded_file_path)

    async def try_analyze(
        self, dto: StrategyGrayLabelTry,
    ) -> StrategyGrayLabelTryResult:
        entity = await self._get_entity(dto.id)
        frame_file_path = join_path_parts(
            entity.path_dir, _FRAMES_DIR, _BASE_FRAME_FULLNAME,
        )
        exists, buffer = await self._storage.read_buffer(frame_file_path)
        if not exists:
            raise GrayLabelMappingException.not_initialized()

        original_frame = decode_frame(buffer)
        frame = original_frame.copy()
        if dto.options.use_tone_filter:
            frame = darken_tone(frame)

        pixels = detect_pixels(
            frame=frame,
            n_pixels=(
                entity.total_pixels + dto.options.score_filter_margin
                if dto.options.use_score_filter else entity.total_pixels
            ),
            quality_levels=dto.options.quality_levels,
            min_distance=dto.options.min_distance,
        )
        if len(pixels) < entity.total_pixels:
            raise GrayLabelMappingException.no_pixel_targets()

        if dto.options.use_score_filter:
            pixels = score_pixels(
                frame=original_frame,
                n_pixels=entity.total_pixels,
                candidates=pixels,
            )

        is_exposed, file_id = await self._expose_file_port.expose(frame_file_path)
        if not is_exposed:
            raise GrayLabelMappingException()

        return StrategyGrayLabelTryResult(
            pixels_file_id=file_id,
            pixels_positions=pixels,
        )

    async def continue_analyze(
        self, dto: StrategyGrayLabelContinue
    ) -> StrategyGrayLabelContinueResult:
        entity = await self._get_entity(dto.id)

        async def _load_frame(frame_idx: int):
            frame_file_path = join_path_parts(
                entity.path_dir, _FRAMES_DIR, format_fullname(frame_idx, _FRAME_EXT),
            )
            is_loaded, buffer = await self._storage.read_buffer(frame_file_path)
            if not is_loaded:
                raise GrayLabelMappingException.not_initialized()

            return decode_frame(buffer)

        n_frames_to_load = get_n_unique_frames_required(entity.total_pixels)
        frames = [
            await _load_frame(frame_idx)
            for frame_idx in range(n_frames_to_load + 1)
        ]

        mapped_position = read_labels(
            frames=frames,
            n_pixels=entity.total_pixels,
            pixels=dto.pixels_positions
        )
        positions = [
            coord for _, coord in sorted(mapped_position.items())
        ]

        if len(positions) != entity.total_pixels:
            raise GrayLabelMappingException.failed_to_read_labels()

        entity.status = Status.MAPPED
        entity.positions = positions
        await self._repository.save(entity)

        return StrategyGrayLabelContinueResult(positions=entity.positions)

    async def _get_entity(self, entity_id: UUID) -> StrategyEntity:
        entity = await self._repository.get(entity_id)
        if entity is None:
            raise StrategyNotFound()

        if entity.strategy != Strategy.GRAY_LABEL:
            raise StrategyUnapplicable()

        return entity
