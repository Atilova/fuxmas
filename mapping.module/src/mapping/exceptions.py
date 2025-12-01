class MappingException(Exception):
    _default_msg: str

    def __init__(self, msg: str | None = None, *args, **kwargs):
        msg = msg or self._default_msg

        super().__init__(msg, *args, **kwargs)

    @classmethod
    def from_exc(cls, exc: Exception):
        return cls(str(exc))


class InvalidStrategy(MappingException):
    _default_msg = "The selected mapping strategy is invalid."


class UnsupportedFileMIME(MappingException):
    _default_msg = "The uploaded file's MIME type is not supported by the selected strategy."


class StrategyNotFound(MappingException):
    _default_msg = "The specified strategy is not found."


class StrategyUnapplicable(MappingException):
    _default_msg = "The specified strategy is unbailable to method used."


class GrayLabelMappingException(MappingException):
    _default_msg = "An error occurred while mapping lights."

    @classmethod
    def not_initialized(cls):
        return cls("The specified strategy is not initialized.")

    @classmethod
    def no_pixel_targets(cls):
        return cls("Unable to detect required number of target pixels.")

    @classmethod
    def failed_to_read_labels(cls):
        return cls("Failed to read all gray labels and restore positions.")


class ExposeFileNotFound(MappingException):
    _default_msg = "The specified file is not found."
