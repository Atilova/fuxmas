from pathlib import Path

import cv2

from pkg.graylabel.exceptions import ClipVideoException
from pkg.graylabel.common import get_n_unique_frames_required


def clip_video(
    file_path: Path,
    *,
    n_pixels: int,
    pattern_interval: float = 1,
):
    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        raise ClipVideoException.failed_to_initialize()

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_step = fps * pattern_interval

    n_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    required_n_frames = get_n_unique_frames_required(n_pixels)
    expected_cap_frames = frame_step * required_n_frames

    if n_frames < expected_cap_frames:
        raise ClipVideoException.not_enough_frames()

    for frame_idx in range(required_n_frames + 1):  # Include base frame
        ret, frame = cap.read()
        if not ret:
            raise ClipVideoException.unexpected_end_of_capture()

        yield frame_idx, frame

        pos = cap.get(cv2.CAP_PROP_POS_FRAMES)
        cap.set(
            cv2.CAP_PROP_POS_FRAMES,
            pos + frame_step,
        )
