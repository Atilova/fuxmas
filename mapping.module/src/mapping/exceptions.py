class MappingException(Exception):
    _default_msg: str

    def __init__(self, msg: str | None = None, *args, **kwargs):
        msg = msg or self._default_msg

        super().__init__(msg, *args, **kwargs)


class InvalidStrategy(MappingException):
    _default_msg = "The selected mapping strategy is invalid."


class UnsupportedFileMIME(MappingException):
    _default_msg = "The uploaded file's MIME type is not supported by the selected strategy."


class StrategyNotFound(MappingException):
    _default_msg = "The specified strategy is not found."
