import os

from typing import NamedTuple
from pathlib import Path

from src.mapping.interfaces import IFile


async def _download_file_in_chunks(file: IFile, chunk_size: int):
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break

        yield chunk


class FilesystemStorageConfig(NamedTuple):
    download_path: str = "/tmp/"
    download_chunk_size = 1024 * 1024


class FilesystemStorage:
    def __init__(self, *, config: FilesystemStorageConfig):
        self._config = config

    async def download(self, file: IFile, filename: str | None = None) -> Path:
        file_path = self._download_path(
            "{name}{extension}".format(
                name=filename or file.name,
                extension=file.extension,
            )
        )
        file_chunks = _download_file_in_chunks(
            file, self._config.download_chunk_size
        )

        with open(file_path, "wb") as sys_file:
            async for bytes_chunk in file_chunks:
                sys_file.write(bytes_chunk)

        return file_path

    async def delete(self, file_path: Path) -> bool:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True

        return False

    def _download_path(self, fullname: str):
        return Path(self._config.download_path).joinpath(fullname)
