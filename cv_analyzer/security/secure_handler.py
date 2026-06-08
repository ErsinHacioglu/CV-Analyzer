from contextlib import contextmanager
from pathlib import Path
from typing import Generator
from uuid import uuid4

from .file_validator import FileValidator

_TEMP_DIR = Path(__file__).resolve().parent.parent / "data" / "temp_upload"


class SecureFileHandler:

    def __init__(self, temp_dir: Path | None = None):
        self.temp_dir = temp_dir or _TEMP_DIR

    @contextmanager
    def temporary_cv_file(self, filename: str, content: bytes) -> Generator[Path, None, None]:
        FileValidator.validate(filename, content)

        self.temp_dir.mkdir(parents=True, exist_ok=True)
        safe_name = f"{uuid4().hex}_{Path(filename).name}"
        temp_path = self.temp_dir / safe_name

        try:
            temp_path.write_bytes(content)
            yield temp_path
        finally:
            if temp_path.exists():
                temp_path.unlink()
