from enum import StrEnum, auto


class Strategy(StrEnum):
    SEQUENTIAL_SCAN = auto()  # No sense?
    GRAY_LABEL = auto()


class Status(StrEnum):
    QUEUED = auto()
    MAPPED = auto()


class GrayLabelStatus(StrEnum):
    CLIPPED = auto()
    ANALYZED = auto()
    MAPPED = auto()


class FileMIME(StrEnum):
    MP4 = "video/mp4"
    MOV = "video/quicktime"
    AVI = "video/x-msvideo"
    JPEG = "image/jpeg"
    PNG = "image/png"
