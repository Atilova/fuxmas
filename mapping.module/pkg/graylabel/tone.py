import cv2
import numpy as np

from pkg.graylabel.constants import (
    UINT8_SCALE,
    FLOAT_SCALE,
    ADJUSTMENT_SCALE,
)


def make_darken_tone(
    *,
    contrast: int = 0,
    highlights: int = 0,
    shadows: int = 0,
    gamma: int = 0,
):
    def _darken_tone(frame: cv2.typing.MatLike) -> cv2.typing.MatLike:
        img_f = frame.astype(np.float32) * FLOAT_SCALE

        # Contrast
        c = (contrast / ADJUSTMENT_SCALE) + 1.0
        img_f = (img_f - 0.5) * c + 0.5
        img_f = np.clip(img_f, 0.0, 1.0)

        # Shadows
        s = shadows / ADJUSTMENT_SCALE
        shadow_mask = 1.0 - img_f
        img_f = img_f + s * shadow_mask * img_f
        img_f = np.clip(img_f, 0.0, 1.0)

        # Highlights
        h = highlights / ADJUSTMENT_SCALE
        highlight_mask = img_f
        img_f = img_f + h * highlight_mask * (1.0 - img_f)
        img_f = np.clip(img_f, 0.0, 1.0)

        # Gamma
        g = gamma / ADJUSTMENT_SCALE
        gamma_value = 1.0 - g
        img_f = img_f ** gamma_value
        img_f = np.clip(img_f, 0.0, 1.0)

        return (img_f * UINT8_SCALE).astype(np.uint8)

    return _darken_tone


darken_tone = make_darken_tone(
    contrast=10,
    highlights=-60,
    shadows=-100,
    gamma=-40,
)
