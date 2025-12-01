import math

import cv2
import numpy as np

from pkg.graylabel.exceptions import EncodeFrameException, DecodeFrameException


def get_n_unique_frames_required(n_pixel: int):
    return math.ceil(math.log2(n_pixel))


def encode_frame(frame: cv2.typing.MatLike, ext: str = ".jpg") -> bytes:
    ret, buffer = cv2.imencode(ext, frame)
    if not ret:
        raise EncodeFrameException.failed()

    return buffer, ext


def decode_frame(buffer: bytes) -> cv2.typing.MatLike:
    frame = cv2.imdecode(
        np.frombuffer(buffer, dtype=np.uint8),
        cv2.IMREAD_COLOR,
    )
    if frame is None:
        raise DecodeFrameException.failed()

    return frame


def number_from_graylabel(label: int) -> int:
    shift, label_n = 1, label
    while (label >> shift) > 0:
        label_n ^= label >> shift
        shift += 1

    return label_n


def number_from_graylabel_bits(bits: list[int]) -> int:
    label = 0
    for bit in bits:
        label = (label << 1) | bit

    number = number_from_graylabel(label)

    return number
