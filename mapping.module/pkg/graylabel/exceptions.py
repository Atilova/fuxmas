class MappingFunctionException(Exception): ...


class ClipVideoException(MappingFunctionException):
    @classmethod
    def failed_to_initialize(cls):
        return cls("Failed to initialize video capture.")

    @classmethod
    def not_enough_frames(cls):
        return cls("Not enough frames available to read.")

    @classmethod
    def unexpected_end_of_capture(cls):
        return cls("Unexpected end of video capture.")


class EncodeFrameException(MappingFunctionException):
    @classmethod
    def failed(cls):
        return cls("Failed to encode frame into bytes.")


class DecodeFrameException(MappingFunctionException):
    @classmethod
    def failed(cls):
        return cls("Failed to decode frame into mat.")


class ReadLabelException(Exception):
    @classmethod
    def frames_count_mismatch(cls):
        return cls("Number of required frames to read given number of pixels is less.")
