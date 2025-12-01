from typing import Any
from pathlib import Path


def format_fullname[T: str](name: T, ext: str) -> str:
    return "{name}{ext}".format(
        name=name,
        ext=ext,
    )


def join_path_parts[T: str](*parts: T) -> str:
    return str(Path(*map(str, parts)))
