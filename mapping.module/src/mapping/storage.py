import shutil
import os
from typing import NamedTuple
from pathlib import Path


from src.mapping.interfaces import IFile
from pkg.file import format_fullname


async def _download_file_in_chunks(file: IFile, chunk_size: int):
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break

        yield chunk


class FilesystemStorageConfig(NamedTuple):
    path: str = "/tmp/storage/"
    download_chunk_size = 1024 * 1024


class FilesystemStorage:
    def __init__(self, *, config: FilesystemStorageConfig):
        self._config = config

    async def exists(self, path: Path) -> bool:
        abs_path = self._filesystem_path(path)
        exists = os.path.exists(abs_path)

        return exists

    async def download_file(self, path: Path, name: str, file: IFile) -> Path:
        file_path = path.joinpath(
            format_fullname(name, file.extension.lower()),
        )
        abs_path = self._filesystem_path(file_path)

        self._ensure_path_dirs(abs_path)
        file_chunks = _download_file_in_chunks(
            file, self._config.download_chunk_size
        )

        with open(abs_path, "wb") as sys_file:
            async for bytes_chunk in file_chunks:
                sys_file.write(bytes_chunk)

        return file_path

    async def save_buffer(self, file_path: Path, buffer: bytes) -> Path:
        abs_path = self._filesystem_path(file_path)
        self._ensure_path_dirs(abs_path)

        with open(abs_path, "wb") as sys_file:
            sys_file.write(buffer)

        return file_path

    async def read_buffer(self, file_path: Path) -> tuple[bool, bytes | None]:
        if not await self.exists(file_path):
            return False, None

        abs_path = self._filesystem_path(file_path)
        with open(abs_path, "rb") as sys_file:
            file_bytes = sys_file.read()

        return True, file_bytes

    async def delete(self, path: Path) -> bool:
        if not await self.exists(path):
            return False

        abs_path = self._filesystem_path(path)
        if abs_path.is_dir():
            shutil.rmtree(abs_path)
        else:
            os.remove(abs_path)

        return True

    def get_local_filesystem_path(self, path: Path) -> Path:
        # TODO: Find a better solution, not to expose full path
        # This is required for cv2.CaptureVideo and FastAPI FileResponse
        return self._filesystem_path(path)

    def _filesystem_path(self, *parts: str | Path) -> Path:
        return Path(self._config.path).joinpath(*parts)

    def _ensure_path_dirs(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
