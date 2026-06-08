from pathlib import Path

ALLOWED_EXTENSIONS = {".pdf", ".txt"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024


class FileValidator:

    @classmethod
    def validate(cls, filename: str, content: bytes) -> None:
        cls._validate_extension(filename)
        cls._validate_size(content)
        cls._validate_content_signature(filename, content)

    @staticmethod
    def _validate_extension(filename: str) -> None:
        suffix = Path(filename).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Sadece pdf ve txt kabul ediliyor. Gönderilen: {suffix or 'uzantı yok'}")

    @staticmethod
    def _validate_size(content: bytes) -> None:
        if len(content) == 0:
            raise ValueError("Boş dosya yüklenemez.")
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise ValueError(f"Dosya 5 MB'dan büyük olamaz.")

    @classmethod
    def _validate_content_signature(cls, filename: str, content: bytes) -> None:
        suffix = Path(filename).suffix.lower()
        if suffix == ".pdf":
            cls._validate_pdf(content)
        elif suffix == ".txt":
            cls._validate_text(content)

    @staticmethod
    def _validate_pdf(content: bytes) -> None:
        if not content.startswith(b"%PDF-"):
            raise ValueError("Geçerli bir PDF değil.")

    @staticmethod
    def _validate_text(content: bytes) -> None:
        null_ratio = content.count(b"\x00") / len(content)
        if null_ratio > 0.01:
            raise ValueError("Txt dosyası binary içerik barındırıyor.")
        try:
            content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("Txt dosyası UTF-8 değil.") from exc
