import cv2
import numpy as np

from pkg.graylabel.constants import (
    UINT8_SCALE,
    DT_BLOCK_SIZE,
    SC_PIXEL_RED_LOW_HUE,
    SC_PIXEL_RED_HIGH_HUE,
    SC_PIXEL_BRIGHT_VAL_THRESHOLD,
    SC_PIXEL_SATURATION_THRESHOLD,
    SC_PIXEL_RED_WEIGHT,
    SC_PIXEL_BRIGHTNESS_WEIGHT,
    SC_PIXEL_RADIUS_RANGE,
    RD_LABEL_RADIUS_RANGE,
)
from pkg.graylabel.common import (
    get_n_unique_frames_required,
    number_from_graylabel_bits,
)
from pkg.graylabel.exceptions import ReadLabelException


type CoordT = tuple[int, int]


def detect_pixels(
    frame: cv2.typing.MatLike,
    n_pixels: int,
    *,
    quality_levels: float = 0.02,
    min_distance: int = 14,
) -> list[CoordT]:
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    tracked = cv2.goodFeaturesToTrack(
        gray_frame,
        maxCorners=n_pixels,
        qualityLevel=quality_levels,
        minDistance=min_distance,
        blockSize=DT_BLOCK_SIZE,
    )

    def _normalize_coord(coord: tuple[float, float]) -> CoordT:
        x, y = coord
        normalized = int(x), int(y)

        return normalized

    return [
        _normalize_coord(coord.ravel())
        for coord in tracked
    ]


def sample_ring_hsv(
    frame: cv2.typing.MatLike,
    coord: CoordT,
    radius_range: tuple[int, int],
    *,
    step_angle: int = 30,
) -> np.ndarray[np.uint8]:
    x, y = coord
    height, width = frame.shape[:2]
    ring_pixels = []

    def _is_within_frame(px: int, py: int):
        return 0 <= px < width and 0 <= py < height

    for radius in range(*radius_range):
        for angle_deg in range(0, 360, step_angle):
            radians = np.radians(angle_deg)
            px = int(x + radius * np.cos(radians))
            py = int(y + radius * np.sin(radians))

            if not _is_within_frame(px, py):
                continue

            ring_pixels.append(frame[py, px])

    return np.array(ring_pixels, dtype=np.uint8)


def get_average_brightness_hsv(
    frame: cv2.typing.MatLike,
    coord: CoordT,
    radius_range: tuple[int, int],
    *,
    step_angle: int = 30,
) -> float:
    ring_pixels = sample_ring_hsv(
        frame=frame,
        coord=coord,
        radius_range=radius_range,
        step_angle=step_angle,
    )

    if not ring_pixels.size:
        return 0.0

    vals = ring_pixels[:, 2]
    average = float(vals.mean())

    return average


def score_pixels(
    frame: cv2.typing.MatLike,
    n_pixels: int,
    candidates: list[CoordT],
) -> list[CoordT]:
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    scores = []
    for coord in candidates:
        ring_pixels = sample_ring_hsv(
            frame=hsv_frame,
            coord=coord,
            radius_range=SC_PIXEL_RADIUS_RANGE,
        )
        if not ring_pixels.size:
            scores.append((coord, 0.0))
            continue

        ring_pixels = np.array(ring_pixels)
        hues, sats, vals = (
            ring_pixels[:, 0],
            ring_pixels[:, 1],
            ring_pixels[:, 2],
        )

        _red_mask = (hues < SC_PIXEL_RED_LOW_HUE) | (hues > SC_PIXEL_RED_HIGH_HUE)
        _bright_mask = vals > SC_PIXEL_BRIGHT_VAL_THRESHOLD
        _saturated_mask = sats > SC_PIXEL_SATURATION_THRESHOLD
        _mask = _red_mask & _bright_mask & _saturated_mask

        red_score = np.sum(_mask) / len(ring_pixels)
        brightness_score = np.mean(vals) / UINT8_SCALE

        total_score = (
            red_score * SC_PIXEL_RED_WEIGHT + brightness_score * SC_PIXEL_BRIGHTNESS_WEIGHT
        )
        scores.append((coord, total_score))

    scores.sort(key=lambda value: value[1], reverse=True)
    top_pixels = [coord for coord, _ in scores[:n_pixels]]

    return top_pixels


def read_labels(
    frames: list[cv2.typing.MatLike],
    n_pixels: int,
    pixels: list[CoordT],
    *,
    on_threshold_scatter: int = 10
) -> dict[int, CoordT]:
    required_n_frames = get_n_unique_frames_required(n_pixels)
    if len(frames) < required_n_frames + 1:
        raise ReadLabelException.frames_count_mismatch()

    base_frame, *rest_frames = frames
    base_frame_hsv = cv2.cvtColor(base_frame, cv2.COLOR_BGR2HSV)
    pixels_brightness_map = {
        coord: get_average_brightness_hsv(
            frame=base_frame_hsv,
            coord=coord,
            radius_range=RD_LABEL_RADIUS_RANGE
        )
        for coord in pixels
    }

    def _read_pixel_state(frame_hsv: cv2.typing.MatLike, coord: CoordT) -> int:
        brightness = get_average_brightness_hsv(
            frame=frame_hsv,
            coord=coord,
            radius_range=RD_LABEL_RADIUS_RANGE
        )
        state = int(brightness >= pixels_brightness_map[coord] - on_threshold_scatter)

        return state

    positions_bits = {coord: [] for coord in pixels}
    for frame_idx in range(required_n_frames):
        frame =  rest_frames[frame_idx]
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        for coord in positions_bits:
            state = _read_pixel_state(frame_hsv, coord)
            positions_bits[coord].append(state)

    positions = {
        number_from_graylabel_bits(reversed(bits)): coord
        for coord, bits in positions_bits.items()
    }

    return positions
